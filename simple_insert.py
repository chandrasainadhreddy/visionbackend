import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='binoculardb')
cur = conn.cursor()

# Get data for test 145
cur.execute("SELECT * FROM tests WHERE id = 145")
test_145 = cur.fetchone()
print(f"Test 145 record: {test_145}")

# Try to insert
print("\nAttempting insert...")
cur.execute("INSERT INTO eye_data (test_id, n, x, y, lx, ly, rx, ry) VALUES (145, 1, 100.0, 200.0, 50.0, 75.0, 150.0, 225.0)")
conn.commit()

cur.execute("SELECT COUNT(*) as cnt FROM eye_data WHERE test_id = 145")
row = cur.fetchone()
print(f"Count after insert: {row[0]}")

conn.close()
print("✅ Done")
