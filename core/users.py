#!/bin/env python3

from db import __core_db__ as coredb

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
    sql = f"SELECT {columns} FROM users WHERE {search_by} = {search_val};"
    conn = coredb.getDBObject()
    cursor = conn.cursor()
    cursor = cursor.execute(sql)
    dat = cursor.fetchall()
    for row in dat:
        for col in row:
            print(col, sep=' ')
        print()
    cursor.close()
    conn.close()
    return sql, dat

def check_auth_info(username, password):
    """
    Check authentication information for logging in.
    Provided Password needs to be in hash only
    returns - the User or None
    """
    pass

# def test_func_table_sel():
#     return __get_cols_from_table(coloumn_names, 2)
