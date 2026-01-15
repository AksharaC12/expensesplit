import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="app_user",          # change if needed
        password="app1234",       # change if needed
        database="expense_split"  # change if needed
    )
