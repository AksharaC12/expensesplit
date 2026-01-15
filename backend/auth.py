from db import get_db_connection


def login_user(email, pin):
    """
    Verifies user credentials.
    Returns user dict if valid, else None
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, full_name, email
        FROM users
        WHERE email = %s AND pin = %s
        """,
        (email, pin)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user


def signup_user(name, email, pin):
    """
    Creates a new user.
    Returns True if created, False if email exists
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check duplicate email
    cursor.execute(
        "SELECT id FROM users WHERE email = %s",
        (email,)
    )

    if cursor.fetchone():
        cursor.close()
        conn.close()
        return False

    # Insert new user
    cursor.execute(
        """
        INSERT INTO users (full_name, email, pin)
        VALUES (%s, %s, %s)
        """,
        (name, email, pin)
    )

    conn.commit()
    cursor.close()
    conn.close()
    return True
