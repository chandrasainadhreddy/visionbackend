from flask import Flask, request, jsonify, render_template_string, url_for
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import datetime as dt
import pandas as pd
import numpy as np
from features import extract_features_by_type 
import os
import joblib
import secrets
import re

# Load environment variables from .env
load_dotenv()

import pymysql
pymysql.install_as_MySQLdb()

# ================= APP INIT =================

app = Flask(__name__)
CORS(app)

app.secret_key = "binocular_secret_key"

# ================= FLASK-MAIL CONFIG =================

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='boggulachandrasainadhreddy4970@gmail.com',
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD', 'ennyjdimqatipkmb'),
    MAIL_DEFAULT_SENDER='boggulachandrasainadhreddy4970@gmail.com'
)

mail = Mail(app)

# ================= DATABASE HELPERS =================

def get_db_connection():
    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="binoculardb",
        cursorclass=pymysql.cursors.DictCursor
    )

bcrypt = Bcrypt(app)

# ================= LOAD MODELS =================

BASE_DIR = os.path.dirname(__file__)
MODELS_DIR = os.path.join(BASE_DIR, "Models")

print("BASE_DIR =", BASE_DIR)
print("MODELS_DIR =", MODELS_DIR)
print("FILES IN MODELS_DIR =", os.listdir(MODELS_DIR) if os.path.exists(MODELS_DIR) else "DIR NOT FOUND")

loaded_models = {}
loaded_scalers = {}

def load_models():
    print("Loading models from:", MODELS_DIR)
    for test_type in ["ran", "pur", "vrg"]:
        model_path = os.path.join(MODELS_DIR, f"model_{test_type}.pkl")
        scaler_path = os.path.join(MODELS_DIR, f"scaler_{test_type}.pkl")

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            loaded_models[test_type.lower()] = joblib.load(model_path)
            loaded_scalers[test_type.lower()] = joblib.load(scaler_path)
            print(f"✅ Loaded {test_type.upper()} model")
        else:
            print(f"❌ Missing files for {test_type.upper()}")
            print(f"   Expected: {model_path}, {scaler_path}")

load_models()

# ✅ One-Shot Live Test (verify model is not flat)
if "ran" in loaded_models and "ran" in loaded_scalers:
    test_feat = np.array([[100, 20, 120, 30]])
    test_score = loaded_models["ran"].decision_function(
        loaded_scalers["ran"].transform(test_feat)
    )
    print(f"🔥 ONE-SHOT TEST: {test_score}")
    if test_score == 0.0:
        print("⚠️  Model score is 0 — model may be flat, retrain required!")
    else:
        print("✅ Model is working (non-zero score)")
else:
    print("⚠️  Skipping one-shot test — RAN model not loaded")

# ================= HOME =================

@app.route("/")
def home():
    return jsonify({"message": "Binocular Vision Backend Running"})


# ================= REGISTER =================

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        # ✅ Check all fields
        if not all([name, email, phone, password, confirm_password]):
            return jsonify({"status": False, "message": "All fields required"})

        # ✅ Confirm password check
        if password != confirm_password:
            return jsonify({"status": False, "message": "Passwords do not match"})

        # ✅ Strong password validation
        # Minimum 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        
        if not re.match(pattern, password):
            return jsonify({
                "status": False,
                "message": "Password must be at least 8 characters and include uppercase, lowercase, number, and special character"
            })

        conn = get_db_connection()
        cur = conn.cursor()

        # ✅ Check if email exists
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cur.fetchone():
            conn.close()
            return jsonify({"status": False, "message": "Email already exists"})

        # ✅ Hash password
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")

        # ✅ Insert user
        cur.execute("""
            INSERT INTO users (name,email,phone,password)
            VALUES (%s,%s,%s,%s)
        """, (name, email, phone, hashed))

        conn.commit()
        conn.close()

        return jsonify({"status": True, "message": "Registration successful"})

    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500

# ================= LOGIN =================

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id,password FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({"status": False, "message": "User not found"})

        if not bcrypt.check_password_hash(user["password"], password):
            return jsonify({"status": False, "message": "Invalid password"})

        return jsonify({
            "status": True,
            "user_id": user["id"]
        })

    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500

# ================= FORGOT PASSWORD =================

@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get("email")

        if not email:
            return jsonify({"status": False, "message": "Email required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"status": False, "message": "Email not found"}), 404

        # Generate token
        token = secrets.token_urlsafe(32)
        expiry = dt.datetime.now() + dt.timedelta(minutes=15)

        cursor.execute("""
            UPDATE users 
            SET reset_token=%s, reset_token_expiry=%s
            WHERE email=%s
        """, (token, expiry, email))
        conn.commit()
        conn.close()

        # ✅ AUTO-DETECT CURRENT SERVER (NO HARDCODE IP)
        reset_link = url_for(
            "reset_password_form",
            token=token,
            _external=True
        )

        # Send Email
        msg = Message(
            subject="Reset Your Password",
            recipients=[email]
        )

        msg.body = f"""
Hello {user['name']},

You requested to reset your password.

Click the link below to reset it:
{reset_link}

This link will expire in 15 minutes.

If you did not request this, please ignore this email.
"""

        mail.send(msg)

        return jsonify({
            "status": True,
            "message": "Reset link sent to your email"
        })

    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500
# ================= RESET PASSWORD =================

@app.route("/reset-password/<token>", methods=["GET"])
def reset_password_form(token):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM users
        WHERE reset_token=%s AND reset_token_expiry > NOW()
    """, (token,))

    user = cursor.fetchone()

    if not user:
        return "<h2 style='color:red;'>Invalid or Expired Token</h2>"

    return render_template_string("""
        <h2>Reset Your Password</h2>
        <form method="POST">
            <input type="password" name="password" placeholder="Enter New Password" required>
            <br><br>
            <button type="submit">Update Password</button>
        </form>
    """)

@app.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    try:
        # ✅ Accept password from browser form OR JSON
        if request.content_type == "application/json":
            data = request.get_json()
            new_password = data.get("password") if data else None
        else:
            new_password = request.form.get("password")

        if not new_password:
            return "<h3 style='color:red;'>Password is required</h3>"

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM users
            WHERE reset_token=%s AND reset_token_expiry > NOW()
        """, (token,))
        user = cursor.fetchone()

        if not user:
            return "<h3 style='color:red;'>Invalid or Expired Token</h3>"

        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")

        cursor.execute("""
            UPDATE users
            SET password=%s,
                reset_token=NULL,
                reset_token_expiry=NULL
            WHERE id=%s
        """, (hashed_password, user["id"]))

        conn.commit()
        conn.close()

        return """
            <h2 style="color:green;">Password updated successfully ✅</h2>
            <p>You can now close this page and login.</p>
        """

    except Exception as e:
        return f"<pre>{str(e)}</pre>", 500

# ================= PROFILE =================

@app.route("/profile")
def profile():
    user_id = request.args.get("user_id")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id,name,email,phone FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()

    if not user:
        conn.close()
        return jsonify({"status": False, "message": "Not found"})
    conn.close()
    return jsonify({"status": True, "user": user})

# ================= UPDATE PROFILE =================

@app.route("/update_profile", methods=["PUT"])
def update_profile():
    try:
        data = request.json

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE users
            SET name=%s,email=%s,phone=%s
            WHERE id=%s
        """, (
            data.get("name"),
            data.get("email"),
            data.get("phone"),
            data.get("user_id")
        ))

        conn.commit()
        conn.close()

        return jsonify({"status": True, "message": "Updated"})

    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500

# ================= START TEST =================

@app.route("/start_test", methods=["POST"])
def start_test():
    try:
        data = request.json
        user_id = data.get("user_id")
        test_type = data.get("test_type").lower()

        if not user_id or not test_type:
            return jsonify({"status": False, "message": "Missing user_id or test_type"})

        conn = get_db_connection()
        cur = conn.cursor()

        # 1️⃣ Check if already running test exists
        cur.execute("""
            SELECT id FROM tests
            WHERE user_id=%s AND test_type=%s AND status='running'
            ORDER BY started_at DESC
            LIMIT 1
        """, (user_id, test_type))

        existing_test = cur.fetchone()

        if existing_test:
            conn.close()
            return jsonify({
                "status": True,
                "test_id": existing_test["id"],
                "message": "Existing running test resumed"
            })

        # 2️⃣ Create new test only if none running
        cur.execute("""
            INSERT INTO tests (user_id,test_type,started_at,status,total_samples)
            VALUES (%s,%s,NOW(),'running',0)
        """, (user_id, test_type))

        conn.commit()
        conn.close()

        return jsonify({
            "status": True,
            "test_id": cur.lastrowid,
            "message": "New test started"
        })

    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500


# ================= UPLOAD EYE DATA =================

@app.route("/upload_eye_data", methods=["POST"])
def upload_eye_data():
    conn = None
    try:
        data = request.json
        test_id = data.get("test_id")
        samples = data.get("samples")

        if not test_id or not samples:
            return jsonify({"status": False, "message": "Missing data"})

        if not isinstance(samples, list) or len(samples) == 0:
            return jsonify({"status": False, "message": "samples must be a non-empty list"})

        rows = []
        for s in samples:
            try:
                rows.append((
                    int(test_id),
                    float(s.get("n", 0)),
                    float(s.get("x", 0)),
                    float(s.get("y", 0)),
                    float(s.get("lx", 0)),
                    float(s.get("ly", 0)),
                    float(s.get("rx", 0)),
                    float(s.get("ry", 0))
                ))
            except (ValueError, TypeError) as ve:
                return jsonify({"status": False, "error": f"Invalid data format: {str(ve)}"}), 400

        conn = get_db_connection()
        cur = conn.cursor()
        
        # ✅ INSERT FIRST with proper error handling
        try:
            cur.executemany("""
                INSERT INTO eye_data
                (test_id,n,x,y,lx,ly,rx,ry)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, rows)
        except Exception as insert_error:
            conn.close()
            return jsonify({
                "status": False, 
                "error": f"Failed to insert eye data: {str(insert_error)}"
            }), 500

        # ✅ UPDATE COUNTER ONLY IF INSERT SUCCEEDED
        try:
            cur.execute("""
                UPDATE tests
                SET total_samples = total_samples + %s
                WHERE id=%s
            """, (len(rows), test_id))
        except Exception as update_error:
            conn.rollback()
            conn.close()
            return jsonify({
                "status": False, 
                "error": f"Failed to update test counter: {str(update_error)}"
            }), 500

        conn.commit()
        conn.close()

        return jsonify({"status": True, "inserted": len(rows)})

    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
            try:
                conn.close()
            except:
                pass
        return jsonify({"status": False, "error": str(e)}), 500

# ================= GET HISTORY =================

# ================= GET HISTORY =================

@app.route("/history", methods=["GET"])
def history():
    try:
        user_id = request.args.get("user_id")

        if not user_id:
            return jsonify({"status": False, "message": "user_id required"})

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                t.id as test_id, 
                t.test_type, 
                t.started_at,
                r.score,
                r.classification,
                r.percentage
            FROM tests t
            LEFT JOIN results r ON t.id = r.test_id
            WHERE t.user_id = %s
            ORDER BY t.started_at DESC
        """, (user_id,))

        rows = cur.fetchall()
        conn.close()

        history_list = []

        for row in rows:
            history_list.append({
                "test_id": row["test_id"],
                "test_type": row["test_type"],
                "started_at": row["started_at"].strftime("%Y-%m-%d %H:%M:%S") if row["started_at"] else None,
                "score": float(row["score"]) if row["score"] is not None else None,
                "percentage": float(row["percentage"]) if row["percentage"] is not None else 0.0,
                "classification": row["classification"] if row["classification"] else "Pending"
            })

        return jsonify({
            "status": True,
            "history": history_list
        })

    except Exception as e:
        return jsonify({"status": False, "error": str(e)}), 500
        
# ================= HOME DASHBOARD =================

@app.route("/home_dashboard", methods=["GET"])
def home_dashboard():
    try:
        user_id = request.args.get("user_id")

        if not user_id:
            return jsonify({"status": False, "message": "user_id required"})

        conn = get_db_connection()
        cursor = conn.cursor()

        # 🔹 Get latest completed test
        cursor.execute("""
            SELECT 
                t.id,
                t.test_type,
                t.started_at,
                r.percentage,
                r.classification
            FROM tests t
            JOIN results r ON t.id = r.test_id
            WHERE t.user_id = %s
            ORDER BY t.started_at DESC
            LIMIT 1
        """, (user_id,))

        latest = cursor.fetchone()

        # 🔹 Get recent 5 tests
        cursor.execute("""
            SELECT 
                t.id,
                t.test_type,
                t.started_at,
                r.percentage,
                r.classification
            FROM tests t
            JOIN results r ON t.id = r.test_id
            WHERE t.user_id = %s
            ORDER BY t.started_at DESC
            LIMIT 5
        """, (user_id,))

        recent_rows = cursor.fetchall()

        recent_tests = []
        for row in recent_rows:
            recent_tests.append({
                "test_id": row["id"],
                "test_type": row["test_type"],
                "started_at": row["started_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "percentage": float(row["percentage"]),
                "classification": row["classification"]
            })

        return jsonify({
            "status": True,
            "latest_test": {
                "percentage": float(latest["percentage"]) if latest else 0,
                "classification": latest["classification"] if latest else None,
                "started_at": latest["started_at"].strftime("%Y-%m-%d %H:%M:%S") if latest else None,
                "test_type": latest["test_type"] if latest else None
            } if latest else None,
            "recent_tests": recent_tests
        })

    except Exception as e:
        return jsonify({"status": False, "error": str(e)})


@app.route("/run_ai", methods=["POST"])
def run_ai():
    try:
        data = request.get_json()
        test_id = data.get("test_id")

        if not test_id:
            return jsonify({"status": False, "error": "Missing test_id"})

        conn = get_db_connection()
        cursor = conn.cursor()

        # -------------------------------------------------
        # 1️⃣ Get test type
        # -------------------------------------------------
        cursor.execute("SELECT test_type FROM tests WHERE id=%s", (test_id,))
        test_row = cursor.fetchone()

        if not test_row:
            conn.close()
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
            conn.close()
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

            elif anomaly_score >= -0.2321:
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

            elif anomaly_score >= -0.2955:
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

        conn.commit()
        conn.close()

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


# ================= GET RESULT =================

@app.route("/get_result")
def get_result():
    test_id = request.args.get("test_id")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT classification, score, percentage,
               stability, tracking, accuracy, reaction
        FROM results WHERE test_id=%s
    """, (test_id,))

    result = cur.fetchone()

    if not result:
        conn.close()
        return jsonify({"status": False, "message": "Result not ready"})
    conn.close()

    return jsonify({
        "status": True,
        "classification": result["classification"],
        "score": float(result["score"]),
        "percentage": float(result["percentage"]),
        "stability": float(result["stability"]),
        "tracking": float(result["tracking"]),
        "accuracy": float(result["accuracy"]),
        "reaction": float(result["reaction"])
    })

# ================= TEST MAIL ENDPOINT =================

@app.route("/test-mail")
def test_mail():
    try:
        msg = Message(
            subject="Test Mail",
            recipients=["boggulachandrasainadhreddy4970@gmail.com"],
            body="Test email from Flask"
        )
        mail.send(msg)
        return "Mail sent successfully!"
    except Exception as e:
        return str(e)

# ================= RUN SERVER =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

