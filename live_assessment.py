import sys
sys.path.append(r"C:\Users\VAMSI BOGGULA\gazebasevr_project\Features")

import mysql.connector
import numpy as np

test_id = int(sys.argv[1])

# ===== DB CONNECTION =====
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="binoculardb"   # ✅ FIXED NAME
)

cursor = conn.cursor(dictionary=True)

# ===== GET TEST TYPE =====
cursor.execute("SELECT test_type FROM tests WHERE id=%s", (test_id,))
test = cursor.fetchone()

if not test:
    print("Needs Attention,-1")
    sys.exit()

test_type = test["test_type"]

# ===== FETCH EYE DATA =====
cursor.execute("""
    SELECT lx, ly, rx, ry
    FROM eye_data
    WHERE test_id=%s
""", (test_id,))

rows = cursor.fetchall()

if len(rows) < 10:
    print("Needs Attention,10")
    sys.exit()

data = np.array([[r["lx"], r["ly"], r["rx"], r["ry"]] for r in rows])

lx, ly, rx, ry = data[:,0], data[:,1], data[:,2], data[:,3]

disparity = np.mean(np.abs(lx - rx))
stability = np.std(lx) + np.std(rx)

# ===== CLASSIFICATION =====

if test_type == "RAN":
    if stability < 0.02:
        result = "Normal Vision"
        score = 85
    elif stability < 0.05:
        result = "Mild Issue"
        score = 60
    else:
        result = "Needs Attention"
        score = 35

elif test_type == "VRG":
    if disparity < 0.03:
        result = "Normal Vision"
        score = 80
    elif disparity < 0.06:
        result = "Mild Issue"
        score = 55
    else:
        result = "Needs Attention"
        score = 30

else:  # PUR
    combined = disparity + stability
    if combined < 0.05:
        result = "Normal Vision"
        score = 90
    elif combined < 0.08:
        result = "Mild Issue"
        score = 65
    else:
        result = "Needs Attention"
        score = 40

# ===== OUTPUT FOR PHP =====
print(f"{result},{score}")
