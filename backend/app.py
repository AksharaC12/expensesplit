from flask import Flask, request, jsonify
from flask_cors import CORS

from auth import login_user, signup_user
from db import get_db_connection

app = Flask(__name__)

# ✅ Proper global CORS (no manual OPTIONS needed)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"]
)


# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)

    email = data.get("email")
    pin = data.get("pin")

    if not email or not pin:
        return jsonify({"error": "Email and PIN required"}), 400

    user = login_user(email, pin)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "user": user
    }), 200


# ================= SIGNUP =================
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True)

    name = data.get("name")
    email = data.get("email")
    pin = data.get("pin")

    if not name or not email or not pin:
        return jsonify({"error": "All fields required"}), 400

    ok = signup_user(name, email, pin)
    if not ok:
        return jsonify({"error": "Email already exists"}), 409

    return jsonify({"message": "Signup successful"}), 201


# ================= CREATE GROUP =================
@app.route("/groups", methods=["POST"])
def create_group():
    data = request.get_json(force=True)

    name = data.get("name")
    user_id = data.get("user_id")

    if not name or not user_id:
        return jsonify({"error": "Group name and user id required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO `groups` (name) VALUES (%s)",
            (name,)
        )
        group_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
            (group_id, user_id)
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"id": group_id}), 201


# ================= GET GROUPS =================
@app.route("/groups/<int:user_id>", methods=["GET"])
def get_groups(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT g.id, g.name
        FROM `groups` g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = %s
    """, (user_id,))

    groups = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(groups), 200


# ================= ADD EXPENSE =================
@app.route("/expenses", methods=["POST"])
def add_expense():
    data = request.get_json(force=True)

    group_id = data.get("group_id")
    description = data.get("description")
    amount = data.get("amount")
    paid_by = data.get("paid_by")

    if not all([group_id, description, amount, paid_by]):
        return jsonify({"error": "Missing expense fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO expenses (group_id, description, amount, paid_by)
            VALUES (%s, %s, %s, %s)
        """, (group_id, description, amount, paid_by))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Expense added"}), 201


# ================= GET SETTLEMENTS =================
@app.route("/settlements/<int:group_id>", methods=["GET"])
def settlements(group_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT u.full_name AS name,
               COALESCE(SUM(
                   CASE
                       WHEN e.paid_by = u.id THEN e.amount
                       ELSE -e.amount
                   END
               ), 0) AS balance
        FROM users u
        JOIN group_members gm ON u.id = gm.user_id
        LEFT JOIN expenses e ON e.group_id = gm.group_id
        WHERE gm.group_id = %s
        GROUP BY u.id
    """, (group_id,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    balances = {row["name"]: float(row["balance"]) for row in rows}
    return jsonify(balances), 200


# ================= SETTLE UP =================
@app.route("/settle", methods=["POST"])
def settle():
    data = request.get_json(force=True)
    group_id = data.get("group_id")

    if not group_id:
        return jsonify({"error": "Group id required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM expenses WHERE group_id = %s",
            (group_id,)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Group settled"}), 200


# ================= RUN =================
if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",  # ✅ IMPORTANT for Flutter Web
        port=5000,
        threaded=True
    )
