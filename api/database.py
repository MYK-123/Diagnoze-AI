import sqlite3
import json
from pathlib import Path
from typing import Generator, Optional, Any, List, Tuple
import db.core

# # Store DB file inside `api/` folder
# DB_PATH = Path(__file__).resolve().parent.parent / "database/diagnoze.sqlite3"
# DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# def get_connection() -> sqlite3.Connection:
#     """Get a new database connection"""
#     conn = sqlite3.connect(str(DB_PATH))
#     conn.row_factory = sqlite3.Row  # Return rows as dictionaries
#     conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
#     return conn

# @contextmanager
# def get_db() -> Generator[sqlite3.Connection, None, None]:
#     """Context manager for database connections"""
#     conn = get_connection()
#     try:
#         yield conn
#     finally:
#         conn.close()


class Database:
    """Database operations wrapper"""
    
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection
        self.cursor = connection.cursor()
    
    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """Execute a query"""
        return self.cursor.execute(query, params)
    
    def executemany(self, query: str, params: List[Tuple]) -> None:
        """Execute multiple queries"""
        self.cursor.executemany(query, params)
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[dict]:
        """Fetch single row as dictionary"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[dict]:
        """Fetch all rows as dictionaries"""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def fetch_scalar(self, query: str, params: Tuple = ()) -> Any:
        """Fetch single scalar value"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        if row:
            return row[0]
        return None
    
    def commit(self) -> None:
        """Commit transaction"""
        self.conn.commit()
    
    def rollback(self) -> None:
        """Rollback transaction"""
        self.conn.rollback()

def init_db() -> None:
    """Initialize database schema"""
    db.core.db_initialize()
    return
    conn = db.core.get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        age INTEGER NOT NULL DEFAULT 18,
        gender TEXT NOT NULL DEFAULT 'prefer_not_to_say',
        account_type TEXT NOT NULL DEFAULT 'user',
        phone TEXT,
        preferences_json TEXT NOT NULL DEFAULT '{}',
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN NOT NULL DEFAULT 1
    )
    """)
    
    # Create sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # Create chat_sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        state TEXT NOT NULL DEFAULT 'welcome',
        symptoms_json TEXT NOT NULL DEFAULT '[]',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # Create chat_messages table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        data_json TEXT,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
    )
    """)
    
    # Create chat_history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        duration TEXT NOT NULL DEFAULT 'N/A',
        symptoms_json TEXT NOT NULL DEFAULT '[]',
        predictions_json TEXT NOT NULL DEFAULT '[]',
        messages_json TEXT NOT NULL DEFAULT '[]',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id)")
    
    conn.commit()
    conn.close()

