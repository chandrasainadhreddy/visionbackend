@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    # Required validation
    if not all([name, email, phone, password, confirm_password]):
        return jsonify({"status": False, "message": "All fields required"})

    # Email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"status": False, "message": "Invalid email format"})

    # Phone validation
    if not re.match(r"^[0-9]{10}$", phone):
        return jsonify({"status": False, "message": "Phone must be 10 digits"})

    # Password strength
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$', password):
        return jsonify({
            "status": False,
            "message": "Password must contain uppercase, lowercase, number & special character"
        })

    if password != confirm_password:
        return jsonify({"status": False, "message": "Passwords do not match"})

    cur = mysql.connection.cursor()

    # Check existing email
    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        return jsonify({"status": False, "message": "Email already registered"})

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Insert user
    cur.execute("""
        INSERT INTO users (name, email, phone, password)
        VALUES (%s, %s, %s, %s)
    """, (name, email, phone, hashed_password))

    mysql.connection.commit()
    user_id = cur.lastrowid

    session['user_id'] = user_id

    return jsonify({
        "status": True,
        "message": "Registration successful",
        "user_id": str(user_id)
    })
