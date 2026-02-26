from flask import Flask, request, jsonify
import subprocess
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# ============================
# DB CONFIG
# ============================

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "binoculardb"
}

# ============================
# START TEST API
# ============================

@app.route("/start_test", methods=["POST"])
def start_test():

    data = request.json
    test_type = data.get("test_type")
    user_id = data.get("user_id")

    if not test_type or not user_id:
        return jsonify({"status": False, "error": "Missing params"})

    # Map to python choice
    choice_map = {
        "RAN": "1",
        "VRG": "2",
        "PUR": "3",
        "1": "1",
        "2": "2",
        "3": "3"
    }

    choice = choice_map.get(str(test_type))

    if not choice:
        return jsonify({"status": False, "error": "Invalid test type"})

    # ============================
    # RUN PYTHON AI SCRIPT
    # ============================

    cmd = [
        "python",
        "live_camera_assessment.py",
        choice,
        str(user_id)
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)

    return jsonify({
        "status": True,
        "output": proc.stdout,
        "error": proc.stderr
    })

# ============================
# HEALTH CHECK
# ============================

@app.route("/")
def home():
    return "AI Server Running"

# ============================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
