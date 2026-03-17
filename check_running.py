import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='binoculardb', cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

cur.execute('SELECT id, test_type, status FROM tests WHERE status="running"')
rows = cur.fetchall()

print('Running tests:')
if rows:
    for r in rows:
        print(f'  Test {r["id"]}: {r["test_type"]}')
else:
    print('  None - all tests are completed')
    
conn.close()
