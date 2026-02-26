import mysql.connector

def check_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="binoculardb"
        )
        print("Connected successfully")
        cursor = conn.cursor()
        
        tables = ['users', 'tests', 'eye_data', 'results']
        for table in tables:
            print(f"\nChecking table: {table}")
            try:
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"  {col[0]} ({col[1]})")
            except Exception as e:
                print(f"  Error checking {table}: {e}")
                
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_db()
