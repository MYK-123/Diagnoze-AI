#!/bin/env python3

import os
import sqlite3

def getDBPath():
    """
    @returns the relative path of database file.
    """

    return ".\\database\\db.db"

def getSchemaPath():
    """
    @returns the relative path of database schema file.
    """

    return ".\\database\\schema.sql"

def getResetSchemaPath():
    """
    @returns the relative path of reset database schema file.
    """

    return ".\\database\\reset_db.sql"

def getDBPathAbs():
    """
    @returns the absolute path of database file. taken by @see getDBPath()
    """
    if not os.path.exists(getDBPath()):
        return None
    return os.path.abspath(getDBPath())


def getDBObject(db:str | None = None):
    return sqlite3.connect(db if db is not None else getDBPath())

def db_initialize():
    with open(getSchemaPath()) as f:
        sql = f.read()
    conn = getDBObject()
    conn.executescript(sql)
    conn.commit()
    conn.close()

def reset_database():
    with open(getResetSchemaPath()) as f:
        sql = f.read()
    conn = getDBObject()
    conn.executescript(sql)
    conn.commit()
    conn.close()
    db_initialize()
