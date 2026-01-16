from flask import Blueprint, request, jsonify
from db import get_db

groups_bp = Blueprint("groups", __name__)

# ================= CREATE GROUP =================
@groups_bp.route("/groups", methods=["POST"])
def create_group():
    data = request.get_json()

    name = data.get("name")
    user_id = data.get("user_id")

    if not name or not user_id:
        return jsonify({"error": "Group name and user id required"}), 400

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            "INSERT INTO expense_groups (name, created_by) VALUES (%s, %s)",
            (name, user_id),
        )
        group_id = cur.lastrowid

        cur.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
            (group_id, user_id),
        )

        db.commit()
        return jsonify({"group_id": group_id}), 201

    finally:
        cur.close()
        db.close()


# ================= GET USER GROUPS =================
@groups_bp.route("/groups/<int:user_id>", methods=["GET"])
def get_groups(user_id):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(
        """
        SELECT g.id, g.name
        FROM expense_groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = %s
        """,
        (user_id,),
    )

    groups = cur.fetchall()
    cur.close()
    db.close()

    return jsonify(groups), 200


# ================= GET GROUP MEMBERS (FIXED ✅) =================
@groups_bp.route("/groups/<int:group_id>/members", methods=["GET"])
def get_group_members(group_id):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(
        """
        SELECT 
            u.id,
            u.full_name AS name,
            u.email
        FROM group_members gm
        JOIN users u ON gm.user_id = u.id
        WHERE gm.group_id = %s
        """,
        (group_id,),
    )

    members = cur.fetchall()
    cur.close()
    db.close()

    return jsonify(members), 200


# ================= ADD MEMBER BY EMAIL =================
@groups_bp.route("/groups/add-member", methods=["POST"])
def add_member_by_email():
    data = request.get_json()

    group_id = data.get("group_id")
    email = data.get("email")

    if not group_id or not email:
        return jsonify({"error": "Group ID and email required"}), 400

    db = get_db()
    cur = db.cursor(dictionary=True)

    try:
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "User not registered"}), 404

        cur.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
            (group_id, user["id"]),
        )

        db.commit()
        return jsonify({"message": "Member added"}), 201

    except Exception as e:
        if "Duplicate entry" in str(e):
            return jsonify({"error": "User already in group"}), 400
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        db.close()


# ================= ADD EXPENSE =================
@groups_bp.route("/expenses", methods=["POST"])
def add_expense():
    data = request.get_json()

    group_id = data.get("group_id")
    description = data.get("description")
    amount = data.get("amount")
    paid_by = data.get("paid_by")

    if not all([group_id, description, amount, paid_by]):
        return jsonify({"error": "Missing expense fields"}), 400

    db = get_db()
    cur = db.cursor()

    try:
        cur.execute(
            """
            INSERT INTO expenses (group_id, paid_by, amount, description)
            VALUES (%s, %s, %s, %s)
            """,
            (group_id, paid_by, amount, description),
        )
        expense_id = cur.lastrowid

        cur.execute(
            "SELECT user_id FROM group_members WHERE group_id=%s",
            (group_id,),
        )
        members = cur.fetchall()

        split = round(float(amount) / len(members), 2)

        for (user_id,) in members:
            cur.execute(
                """
                INSERT INTO expense_splits (expense_id, user_id, amount)
                VALUES (%s, %s, %s)
                """,
                (expense_id, user_id, split),
            )

        db.commit()
        return jsonify({"message": "Expense added"}), 201

    finally:
        cur.close()
        db.close()


# ================= SETTLEMENTS (FIXED ✅) =================
@groups_bp.route("/settlements/<int:group_id>", methods=["GET"])
def settlements(group_id):
    db = get_db()
    cur = db.cursor(dictionary=True)

    cur.execute(
        """
        SELECT 
            u.full_name AS name,
            SUM(
                CASE
                    WHEN e.paid_by = u.id THEN es.amount
                    ELSE -es.amount
                END
            ) AS balance
        FROM users u
        JOIN expense_splits es ON u.id = es.user_id
        JOIN expenses e ON es.expense_id = e.id
        WHERE e.group_id = %s
        GROUP BY u.id
        """,
        (group_id,),
    )

    result = cur.fetchall()
    cur.close()
    db.close()

    return jsonify(result), 200
