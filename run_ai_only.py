import sys
import numpy as np
import MySQLdb
import joblib

# =========================
# READ ARGUMENT
# =========================
test_id = int(sys.argv[1])

# =========================
# DB CONNECT
# =========================
db = MySQLdb.connect(
    host="localhost",
    user="root",
    passwd="",
    db="binoculardb"
)

cur = db.cursor()

# =========================
# LOAD DATA
# =========================
cur.execute("""
    SELECT n,x,y,lx,ly,rx,ry
    FROM eye_data
    WHERE test_id=%s
""", (test_id,))

rows = cur.fetchall()

if not rows:
    print("No eye data found")
    sys.exit()

data = np.array(rows)

# =========================
# FEATURE EXTRACTION
# =========================
features = [
    np.mean(data[:,1]),
    np.std(data[:,1]),
    np.mean(data[:,2]),
    np.std(data[:,2]),
]

features = np.array(features).reshape(1,-1)

# =========================
# LOAD MODEL
# =========================
model = joblib.load("model.pkl")

score = float(model.predict_proba(features)[0][1])

# =========================
# CLASSIFICATION LABEL
# =========================
def categorize(score):
    if score < 0.4:
        return "normal"
    elif score < 0.7:
        return "mild issue"
    else:
        return "needs attention"

label = categorize(score)

# =========================
# SAVE RESULT
# =========================
cur.execute("""
INSERT INTO results (test_id, score, classification)
VALUES (%s,%s,%s)
ON DUPLICATE KEY UPDATE
score=%s, classification=%s
""", (test_id, score, label, score, label))

db.commit()

print("AI result saved:", label)
