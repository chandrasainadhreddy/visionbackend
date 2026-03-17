import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='binoculardb', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

print("=" * 60)
print("TESTS WITH EYE DATA STATUS")
print("=" * 60)

cur.execute("""
    SELECT t.id, t.test_type, t.status, COUNT(e.id) as sample_count 
    FROM tests t 
    LEFT JOIN eye_data e ON t.id=e.test_id 
    GROUP BY t.id 
    ORDER BY t.id DESC
""")

for row in cur.fetchall():
    status = "✅" if row['sample_count'] > 0 else "❌"
    print(f"{status} Test {row['id']}: {row['test_type']} ({row['status']}) - {row['sample_count']} samples")

conn.close()
