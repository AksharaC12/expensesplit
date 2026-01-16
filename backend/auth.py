from flask import Blueprint, request, jsonify
from db import get_db

auth_bp = Blueprint("auth", __name__)

# ---------------- SIGNUP ----------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    full_name = data.get("name")   # frontend sends "name"
    email = data.get("email")
    pin = data.get("pin")

    if not full_name or not email or not pin:
        return jsonify({"error": "Missing fields"}), 400

    db = get_db()
    cur = db.cursor(dictionary=True)

    # Check duplicate email
    cur.execute("SELECT id FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        cur.close()
        db.close()
        return jsonify({"error": "Email already exists"}), 409

    # Insert user (USE full_name COLUMN)
    cur.execute(
        "INSERT INTO users (full_name, email, pin) VALUES (%s, %s, %s)",
        (full_name, email, pin)
    )
    db.commit()

    user_id = cur.lastrowid
    cur.close()
    db.close()

    return jsonify({"user_id": user_id}), 201


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    pin = data.get("pin")

    if not email or not pin:
        return jsonify({"error": "Missing credentials"}), 400

    db = get_db()
    cur = db.cursor(dictionary=True)

    # ✅ USE full_name, NOT name
    cur.execute(
        "SELECT id, full_name FROM users WHERE email=%s AND pin=%s",
        (email, pin)
    )
    user = cur.fetchone()

    cur.close()
    db.close()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "user_id": user["id"],
        "name": user["full_name"]  # frontend expects "name"
    })
