from db.connection import get_db

def save_result(test_id, score, severity, description):
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO results (test_id, score, severity, description)
        VALUES (%s, %s, %s, %s)
    """, (test_id, score, severity, description))

    cur.execute("""
        UPDATE tests
        SET status='completed', completed_at=NOW()
        WHERE id=%s
    """, (test_id,))

    db.commit()
    db.close()
