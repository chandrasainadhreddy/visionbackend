@app.route('/profile', methods=['GET'])
def profile():

    if 'user_id' not in session:
        return jsonify({"status": False, "message": "Unauthorized"})

    user_id = session['user_id']

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, phone FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()

    if not user:
        return jsonify({"status": False, "message": "User not found"})

    return jsonify({
        "status": True,
        "user": {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "phone": user[3]
        }
    })
