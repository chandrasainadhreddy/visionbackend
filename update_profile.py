@app.route('/update_profile', methods=['POST'])
def update_profile():

    if 'user_id' not in session:
        return jsonify({"status": False, "message": "Unauthorized"})

    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()

    if not name or not phone:
        return jsonify({"status": False, "message": "All fields required"})

    if not re.match(r"^[0-9]{10}$", phone):
        return jsonify({"status": False, "message": "Phone must be 10 digits"})

    user_id = session['user_id']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE users
        SET name=%s, phone=%s
        WHERE id=%s
    """, (name, phone, user_id))

    mysql.connection.commit()

    return jsonify({
        "status": True,
        "message": "Profile updated successfully"
    })
q