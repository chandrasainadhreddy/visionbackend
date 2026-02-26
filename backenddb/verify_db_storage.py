import mysql.connector
import sys
import os

def check_storage():
    print("=== Binocular Vision Database Storage Verification ===")
    
    # 1. Test Connection
    print("\n[1/3] Testing MySQL Connection...")
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="binoculardb"
        )
        print("[SUCCESS] Connection Successful!")
    except mysql.connector.Error as err:
        print(f"[FAILURE] Connection Failed: {err}")
        print("\nPlease ensure XAMPP MySQL is running and the 'binoculardb' database exists.")
        return

    cursor = conn.cursor(dictionary=True)

    # 2. Check Tables
    print("\n[2/3] Checking Table Schema...")
    required_tables = ['users', 'tests', 'eye_data', 'results']
    cursor.execute("SHOW TABLES")
    existing_tables = [list(row.values())[0] for row in cursor.fetchall()]
    
    for table in required_tables:
        if table in existing_tables:
            print(f"[OK] Table '{table}' exists.")
        else:
            print(f"[MISSING] Table '{table}' is MISSING.")

    # 3. Check Data Counts
    print("\n[3/3] Scanning Data Volume...")
    for table in required_tables:
        if table in existing_tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            print(f"[DATA] {table}: {count} records found.")

    cursor.close()
    conn.close()
    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    check_storage()
