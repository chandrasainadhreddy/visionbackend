@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"status": False, "message": "All fields required"})

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, password FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    if user:
        user_id, hashed_password = user

        if bcrypt.check_password_hash(hashed_password, password):
            session['user_id'] = user_id
            return jsonify({
                "status": True,
                "message": "Login successful",
                "user_id": str(user_id)
            })

    return jsonify({"status": False, "message": "Invalid credentials"})
