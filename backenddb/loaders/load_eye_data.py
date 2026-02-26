import pandas as pd
from db.connection import get_db

def load_eye_data(test_id):
    db = get_db()
    query = """
        SELECT x, y, lx, ly, rx, ry
        FROM eye_data
        WHERE test_id = %s
        ORDER BY n ASC
    """
    df = pd.read_sql(query, db, params=(test_id,))
    db.close()
    return df
