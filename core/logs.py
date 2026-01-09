#!/bin/env python3

from db import core as coredb

class Log:

    def __init__(self, log_id, user_id, action_type, created_at):
        self.log_id = log_id
        self.user_id = user_id
        self.action_type = action_type
        self.created_at = created_at

coloumn_names = ["log_id", "user_id", "action_type", "created_at"]

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

def get_all_logs() -> list[Log]:
    log_s = []
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor = cursor.execute("SELECT log_id, user_id, action_type, created_at FROM logs;")
        dat = cursor.fetchall()
        if dat:
            for dataOne in dat:
                if dataOne:
                    pred = Log(dataOne[0], dataOne[1], dataOne[2], dataOne[3])
                    log_s.append(pred)
    except Exception as e:
        print(f"Error retrieving all logs from logs table: {e}")
    conn.close()
    return log_s

def add_new_log(user_id, action_type) -> bool:
    conn = coredb.getDBObject()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO logs (user_id, action_type) VALUES (?, ?)",
            (user_id, action_type)
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating log: {e}")
        conn.rollback()
        conn.close()
        return False

