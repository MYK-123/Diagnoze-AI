#!/bin/env python3

import sqlite3

DB_PATH = ".\\database\\db.db"  # Your single production/dev DB

def getDBObject():
    return sqlite3.connect(DB_PATH)

def init_db():
    """
    Ensure required tables exist in the database.
    """
    conn = getDBObject()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # User session table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_session (
        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL,
        expires_at DATETIME NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized or verified successfully")
