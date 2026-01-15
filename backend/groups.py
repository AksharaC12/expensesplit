from flask import Blueprint, request, jsonify
from db import get_db_connection

groups_bp = Blueprint("groups", __name__)


# ================= CREATE GROUP =================
@groups_bp.route("/groups", methods=["POST"])
def create_group():
    data = request.get_json()

    name = data.get("name")
    user_id = data.get("user_id")

    if not name or not user_id:
        return jsonify({"error": "Group name and user id required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Create group
    cursor.execute(
        "INSERT INTO groups (name, created_by) VALUES (%s, %s)",
        (name, user_id)
    )
    group_id = cursor.lastrowid

    # Add creator as member
    cursor.execute(
        "INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)",
        (group_id, user_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Group created"}), 201


# ================= GET USER GROUPS =================
@groups_bp.route("/groups/<int:user_id>", methods=["GET"])
def get_groups(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT g.id, g.name
        FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = %s
        """,
        (user_id,)
    )

    groups = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(groups), 200
