import mysql.connector
import sys

def get_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="binoculardb"
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}", file=sys.stderr)
        return None
