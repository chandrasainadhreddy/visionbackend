from flask import Flask, request, jsonify
from db.connection import get_db

from services.ran_service import run_ran
from services.vrg_service import run_vrg
from services.pur_service import run_pur

app = Flask(__name__)

@app.route("/api/test/start", methods=["POST"])
def start_test():
    try:
        data = request.json
        if not data or "user_id" not in data or "test_type" not in data:
            return jsonify({"error": "Missing user_id or test_type"}), 400
            
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO tests (user_id, test_type, status, started_at)
            VALUES (%s, %s, 'running', NOW())
        """, (data["user_id"], data["test_type"]))
        db.commit()
        test_id = cur.lastrowid
        cur.close()
        db.close()
        return jsonify({"test_id": test_id, "duration": 120})
    except Exception as e:
        print(f"Error starting test: {e}")
        return jsonify({"error": "Failed to start test", "details": str(e)}), 500


@app.route("/api/eye-data", methods=["POST"])
def save_eye_data():
    try:
        d = request.json
        if not d or "test_id" not in d:
            return jsonify({"error": "Missing test_id"}), 400
            
        db = get_db()
        cur = db.cursor()
        cur.execute("""
            INSERT INTO eye_data (test_id, n, x, y, lx, ly, rx, ry)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (d["test_id"], d.get("n", 0), d.get("x", 0), d.get("y", 0), d.get("lx", 0), d.get("ly", 0), d.get("rx", 0), d.get("ry", 0)))
        db.commit()
        cur.close()
        db.close()
        return jsonify({"status": "saved"})
    except Exception as e:
        print(f"Error saving eye data: {e}")
        return jsonify({"error": "Failed to save eye data", "details": str(e)}), 500


@app.route("/api/test/ran", methods=["POST"])
def ran():
    return jsonify(run_ran(request.json["test_id"]))


@app.route("/api/test/vrg", methods=["POST"])
def vrg():
    return jsonify(run_vrg(request.json["test_id"]))


@app.route("/api/test/pur", methods=["POST"])
def pur():
    return jsonify(run_pur(request.json["test_id"]))


if __name__ == "__main__":
    app.run(debug=True)
