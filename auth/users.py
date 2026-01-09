#!/bin/env python3

from db import core as coredb

ROLE_USER = "user"
ROLE_MEDICAL_STUDENT = "medical_student"
ROLE_ADMIN = "admin"

class User:

    def __init__(self, uid, username, email, role):
        self.user_id = uid
        self.username = username
        self.email = email
        self.role = role


coloumn_names = ["user_id", "username", "email", "password", "role",  "created_at"]

def __get_cols_from_table(cols: list[str], search_val:str, search_by:str = "user_id"):
    columns = ", ".join(cols)
    sql = f"SELECT {columns} FROM logs WHERE {search_by} = {search_val};"
    conn = coredb.getDBObject()
    cursor = conn.cursor()
    cursor = cursor.execute(sql)
    dat = cursor.fetchall()
    cursor.close()
    conn.close()
    return sql, dat

def check_auth_info(username, password):
    """
    Check authentication information for logging in.
    Provided Password needs to be in hash only
    returns - the User or None
    """

    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("""
            SELECT user_id, username, email, role FROM users
            WHERE username = ? AND password = ?;
            """, (username, password))
        dat = cursor.fetchone()
        conn.close()
        if dat:
            user = User(uid=dat[0], username=dat[1], email=dat[2], role=dat[3])
            return user
        else:
            return None
    except Exception as e:
        print("Error checking auth info:", e)
        conn.close()
        return None


def add_user_to_db(username, email, password_hash):
    """
    Add a new user to the database.
    Provided Password needs to be in hash only
    returns - success status
    """

    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?);
            """, (username, email, password_hash))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Error adding user to DB:", e)
        conn.rollback()
        conn.close()
        return False
    return True

def update_user_role(user_id, new_role) -> bool:
    """
    Update the role of a user.
    returns - success status
    """

    if new_role not in [ROLE_USER, ROLE_MEDICAL_STUDENT, ROLE_ADMIN]:
        return False

    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("""
            UPDATE users
            SET role = ?
            WHERE user_id = ?;
            """, (new_role, user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Error updating user role:", e)
        conn.rollback()
        conn.close()
        return False
    return True


def delete_user(user_id) -> bool:
    """
    Delete a user from the database.
    returns - success status
    """
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("""
            DELETE FROM users
            WHERE user_id = ?;
            """, (user_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print("Error deleting user:", e)
        conn.rollback()
        conn.close()
        return False
    return True

def get_user_by_id(user_id) -> User | None:
    """
    Retrieve a user by their user ID.
    returns - the User or None
    """

    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("""
            SELECT user_id, username, email, role FROM users
            WHERE user_id = ?;
            """, (user_id,))
        dat = cursor.fetchone()
        conn.close()
        if dat:
            user = User(uid=dat[0], username=dat[1], email=dat[2], role=dat[3])
            return user
        else:
            return None
    except Exception as e:
        print("Error retrieving user by ID:", e)
        conn.close()
        return None

