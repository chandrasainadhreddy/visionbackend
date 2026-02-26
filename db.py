from flask_mysqldb import MySQL

mysql = MySQL()



@app.route("/run_ai", methods=["POST"])
def run_ai():
    try:
        data = request.get_json()
        test_id = data.get("test_id")

        if not test_id:
            return jsonify({"status": False, "error": "Missing test_id"})

        cursor = mysql.connection.cursor()

        # -------------------------------------------------
        # 1️⃣ Get test type
        # -------------------------------------------------
        cursor.execute("SELECT test_type FROM tests WHERE id=%s", (test_id,))
        test_row = cursor.fetchone()

        if not test_row:
            return jsonify({"status": False, "error": "Invalid test_id"})

        test_type = str(test_row["test_type"]).strip().lower()

        if test_type not in loaded_models:
            return jsonify({"status": False, "error": "Model not found"})

        # -------------------------------------------------
        # 2️⃣ Fetch eye data
        # -------------------------------------------------
        cursor.execute("""
            SELECT x, y
            FROM eye_data
            WHERE test_id=%s
            ORDER BY n ASC
        """, (test_id,))
        rows = cursor.fetchall()

        if not rows:
            return jsonify({"status": False, "error": "No eye data found"})

        df = pd.DataFrame(rows)

        # -------------------------------------------------
        # 3️⃣ Feature Engineering
        # -------------------------------------------------
        df["dx"] = df["x"].diff().fillna(0)
        df["dy"] = df["y"].diff().fillna(0)
        df["speed"] = np.sqrt(df["dx"]**2 + df["dy"]**2)

        mean_speed = df["speed"].mean()
        std_speed  = df["speed"].std()
        std_x      = df["x"].std()
        std_y      = df["y"].std()

        features = np.array([[mean_speed, std_speed, std_x, std_y]])

        scaler = loaded_scalers[test_type]
        model  = loaded_models[test_type]

        features_scaled = scaler.transform(features)

        anomaly_score = float(model.decision_function(features_scaled)[0])

        # -------------------------------------------------
        # 4️⃣ Score → Percentage Mapping Function
        # -------------------------------------------------
        def map_score(score, min_score, max_score, min_percent, max_percent):
            if max_score == min_score:
                return min_percent
            score = max(min_score, min(score, max_score))
            ratio = (score - min_score) / (max_score - min_score)
            return round(min_percent + ratio * (max_percent - min_percent), 2)

        # -------------------------------------------------
        # 5️⃣ Classification + Percentage Per Test
        # -------------------------------------------------

        if test_type == "ran":

            if anomaly_score >= -0.2220:
                classification = "Normal"
                percentage = map_score(anomaly_score, -0.2220, -0.15, 95, 100)

            elif anomaly_score >= -0.2295:
                classification = "Mild Issue"
                percentage = map_score(anomaly_score, -0.2295, -0.2220, 86, 94)

            else:
                classification = "Needs Attention"
                percentage = map_score(anomaly_score, -0.30, -0.2295, 74, 85)

            # RAN Metrics (focus on saccadic speed stability)
            tracking  = round(max(0, min(100, percentage - (std_speed * 2))), 2)
            accuracy  = round(max(0, min(100, percentage - ((std_x + std_y) * 1.5))), 2)
            reaction  = round(max(0, min(100, percentage - (std_speed * 3))), 2)

        elif test_type == "vrg":

            if anomaly_score >= -0.3428:
                classification = "Normal"
                percentage = map_score(anomaly_score, -0.3428, -0.30, 95, 100)

            elif anomaly_score >= -0.3431:
                classification = "Mild Issue"
                percentage = map_score(anomaly_score, -0.3431, -0.3428, 86, 94)

            else:
                classification = "Needs Attention"
                percentage = map_score(anomaly_score, -0.36, -0.3431, 74, 85)

            # VRG Metrics (vergence stability important)
            tracking  = round(max(0, min(100, percentage - (std_x * 2))), 2)
            accuracy  = round(max(0, min(100, percentage - (std_y * 2))), 2)
            reaction  = round(max(0, min(100, percentage - (std_speed * 2))), 2)

        elif test_type == "pur":

            if anomaly_score >= -0.2920:
                classification = "Normal"
                percentage = map_score(anomaly_score, -0.2920, -0.26, 95, 100)

            elif anomaly_score >= -0.2940:
                classification = "Mild Issue"
                percentage = map_score(anomaly_score, -0.2940, -0.2920, 86, 94)

            else:
                classification = "Needs Attention"
                percentage = map_score(anomaly_score, -0.31, -0.2940, 74, 85)

            # PUR Metrics (smooth pursuit smoothness)
            tracking  = round(max(0, min(100, percentage - (mean_speed * 1.5))), 2)
            accuracy  = round(max(0, min(100, percentage - ((std_x + std_y) * 2))), 2)
            reaction  = round(max(0, min(100, percentage - (std_speed * 2.5))), 2)

        else:
            return jsonify({"status": False, "error": "Invalid test type"})

        # Stability = overall AI stability
        stability = percentage

        # -------------------------------------------------
        # 6️⃣ Save Results
        # -------------------------------------------------
        cursor.execute("SELECT result_id FROM results WHERE test_id=%s", (test_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE results SET
                    test_type=%s,
                    classification=%s,
                    score=%s,
                    percentage=%s,
                    stability=%s,
                    tracking=%s,
                    accuracy=%s,
                    reaction=%s
                WHERE test_id=%s
            """, (
                test_type, classification, anomaly_score,
                percentage, stability, tracking,
                accuracy, reaction, test_id
            ))
        else:
            cursor.execute("""
                INSERT INTO results (
                    test_id, test_type, classification,
                    score, percentage,
                    stability, tracking, accuracy, reaction
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                test_id, test_type, classification,
                anomaly_score, percentage,
                stability, tracking, accuracy, reaction
            ))

        cursor.execute("""
            UPDATE tests
            SET status='completed', completed_at=NOW()
            WHERE id=%s
        """, (test_id,))

        mysql.connection.commit()

        return jsonify({
            "status": True,
            "test_id": test_id,
            "test_type": test_type,
            "classification": classification,
            "percentage": percentage,
            "stability": stability,
            "tracking": tracking,
            "accuracy": accuracy,
            "reaction": reaction,
            "anomaly_score": anomaly_score
        })

    except Exception as e:
        return jsonify({"status": False, "error": str(e)})