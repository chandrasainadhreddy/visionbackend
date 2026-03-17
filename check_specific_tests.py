import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='binoculardb', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

print("=" * 70)
print("CHECKING EYE DATA FOR TESTS 140-170")
print("=" * 70)

# Check specific ranges
for test_id in [144, 145, 146, 155, 156, 166, 167, 168, 169]:
    cur.execute('SELECT COUNT(*) as count FROM eye_data WHERE test_id = %s', (test_id,))
    result = cur.fetchone()
    count = result['count'] if result else 0
    status = "✅" if count > 0 else "❌"
    print(f"{status} Test {test_id}: {count} samples")

print("\n" + "=" * 70)
print("CHECKING TESTS TABLE")
print("=" * 70)

cur.execute('''
    SELECT id, test_type, status, total_samples 
    FROM tests 
    WHERE id IN (144, 145, 146, 155, 156, 166, 167, 168, 169)
    ORDER BY id
''')

for row in cur.fetchall():
    print(f"Test {row['id']}: {row['test_type']} ({row['status']}) - total_samples field = {row['total_samples']}")

print("\n" + "=" * 70)
print("CHECKING MIN/MAX test_id IN eye_data")
print("=" * 70)

cur.execute('SELECT MIN(test_id) as min_id, MAX(test_id) as max_id FROM eye_data')
result = cur.fetchone()
print(f"Min test_id: {result['min_id']}")
print(f"Max test_id: {result['max_id']}")

conn.close()
