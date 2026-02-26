import os
import sys
import time
import csv
import cv2
import numpy as np
import joblib
import mediapipe as mp
import pandas as pd
import mysql.connector
from datetime import datetime

# =====================================================
# ARGUMENTS
# python live_camera_assessment.py 1 11
# =====================================================
if len(sys.argv) < 3:
    print("Usage: python live_camera_assessment.py <test_choice> <user_id>")
    sys.exit(1)

choice = sys.argv[1]
user_id = int(sys.argv[2])

# =====================================================
# DB CONNECT
# =====================================================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="binoculardb"
)

cursor = db.cursor()

# =====================================================
# PATH SETUP
# =====================================================
BASE_DIR = os.getcwd()
TEMP_DIR = os.path.join(BASE_DIR, "temp")
FEATURES_DIR = os.path.join(BASE_DIR, "Features")
MODELS_DIR = os.path.join(BASE_DIR, "Models")

os.makedirs(TEMP_DIR, exist_ok=True)
sys.path.append(FEATURES_DIR)

# =====================================================
# TEST SELECTION
# =====================================================
DURATION_SEC = 120

if choice == "1":
    test_name = "RAN"
    model_file = os.path.join(MODELS_DIR, "model_ran.pkl")
    scaler_file = os.path.join(MODELS_DIR, "scaler_ran.pkl")
    from ran_features import extract_ran_features as extract_features

elif choice == "2":
    test_name = "VRG"
    model_file = os.path.join(MODELS_DIR, "model_vrg.pkl")
    scaler_file = os.path.join(MODELS_DIR, "scaler_vrg.pkl")
    from vrg_features import extract_vrg_features as extract_features

elif choice == "3":
    test_name = "PUR"
    model_file = os.path.join(MODELS_DIR, "model_pur.pkl")
    scaler_file = os.path.join(MODELS_DIR, "scaler_pur.pkl")
    from pur_features import extract_pur_features as extract_features

else:
    print("Invalid test choice")
    sys.exit(1)

# =====================================================
# SCORE → LABEL FUNCTION
# =====================================================
def categorize(score):
    if score > 0.05:
        return "Normal Vision"
    elif score > -0.1:
        return "Mild Issue"
    else:
        return "Needs Attention"

# =====================================================
# CREATE TEST RECORD
# =====================================================
start_time_db = datetime.now()

cursor.execute("""
INSERT INTO tests (user_id, test_type, started_at, status, total_samples)
VALUES (%s,%s,%s,%s,%s)
""", (user_id, test_name, start_time_db, "running", 0))

db.commit()
test_id = cursor.lastrowid

print("TEST_ID:", test_id)

# =====================================================
# LOAD MODEL
# =====================================================
print("Loading model...")
model = joblib.load(model_file)
scaler = joblib.load(scaler_file)

# =====================================================
# CSV FILE
# =====================================================
final_csv = os.path.join(TEMP_DIR, f"subject_{test_id}.csv")

# =====================================================
# CAMERA START
# =====================================================
print(f"Starting {test_name} test for 2 minutes")

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(refine_landmarks=True)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera not accessible")
    sys.exit(1)

start_time = time.time()
sample_count = 0

with open(final_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["n","x","y","lx","ly","rx","ry"])

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        if result.multi_face_landmarks:

            face = result.multi_face_landmarks[0]
            h, w, _ = frame.shape

            lx = int(face.landmark[468].x * w)
            ly = int(face.landmark[468].y * h)
            rx = int(face.landmark[473].x * w)
            ry = int(face.landmark[473].y * h)

            x = (lx + rx) / 2
            y = (ly + ry) / 2
            t = int((time.time() - start_time) * 1000)

            writer.writerow([t,x,y,lx,ly,rx,ry])

            # ===== SAVE TO DB eye_data =====
            cursor.execute("""
            INSERT INTO eye_data (test_id,n,x,y,lx,ly,rx,ry)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (test_id,t,x,y,lx,ly,rx,ry))

            sample_count += 1

        if time.time() - start_time >= DURATION_SEC:
            break

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
db.commit()

print("Camera recording finished")
print("Samples collected:", sample_count)

# =====================================================
# FEATURE EXTRACTION
# =====================================================
print("Extracting features...")
df = pd.read_csv(final_csv)

if test_name == "RAN":
    ran_csv = os.path.join(TEMP_DIR, f"ran_{test_id}.csv")
    df[["n","x","y"]].to_csv(ran_csv, index=False)
    features = extract_features(ran_csv)
else:
    features = extract_features(df)

# =====================================================
# PREDICTION
# =====================================================
print("Running model prediction...")
X = scaler.transform(np.array([features]))
score = float(model.decision_function(X)[0])

classification = categorize(score)

print("Score:", score)
print("Result:", classification)

# =====================================================
# SAVE RESULT
# =====================================================
cursor.execute("""
INSERT INTO results (test_id, classification, score, ai_notes)
VALUES (%s,%s,%s,%s)
""", (test_id, classification, score, "AI auto result"))

# =====================================================
# UPDATE TEST COMPLETE
# =====================================================
cursor.execute("""
UPDATE tests
SET completed_at=%s, status=%s, total_samples=%s
WHERE id=%s
""", (datetime.now(), "completed", sample_count, test_id))

db.commit()

print("Saved to database successfully")
print("TEST COMPLETE")

cursor.close()
db.close()
