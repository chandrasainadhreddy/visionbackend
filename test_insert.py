import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='binoculardb')
cur = conn.cursor()

print("Attempting to insert test data into test_id 145...")

try:
    cur.execute("""
        INSERT INTO eye_data (test_id, n, x, y, lx, ly, rx, ry)
        VALUES (145, 1, 100.0, 200.0, 50.0, 75.0, 150.0, 225.0)
    """)
    conn.commit()
    print("✅ Insert succeeded!")
    
    cur.execute("SELECT COUNT(*) as count FROM eye_data WHERE test_id = 145")
    result = cur.fetchone()
    print(f"Row count for test_id 145: {result[0]}")
    
except Exception as e:
    print(f"❌ Insert failed: {e}")
    conn.rollback()

conn.close()
