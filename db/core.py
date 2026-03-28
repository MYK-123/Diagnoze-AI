#!/bin/env python3

import os
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Any, List, Tuple

# Store DB file inside `database/` folder
DB_PATH = Path(__file__).resolve().parent.parent / "database/diagnoze.sqlite3"
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"


def getDBPath():
    """
    @returns the relative path of database file.
    """

    return ".\\database\\diagnoze.sqlite3"

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

def getSymptomsPath():
    """
    @returns the relative path of symptoms database schema file.
    """

    return ".\\database\\symptoms.sql"

def getDiseasesPath():
    """
    @returns the relative path of diseases database schema file.
    """

    return ".\\database\\disease.sql"

def getDiseasesSymptomRelationPath():
    """
    @returns the relative path of DiseasesSymptomRelation database schema file.
    """

    return ".\\database\\disease_symptoms.sql"

def getEducationalContentPath():
    """
    @returns the relative path of educational_content database schema file.
    """

    return ".\\database\\educational_content.sql"


def getDBPathAbs():
    """
    @returns the absolute path of database file. taken by @see getDBPath()
    """
    if not os.path.exists(getDBPath()):
        return None
    return os.path.abspath(getDBPath())


def getDBObject(db:str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db if db is not None else getDBPath(), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn
    

def get_connection(db:str | None = None) -> sqlite3.Connection:
    """Get a new database connection Same as getgetDBObject("db path")"""
    return getDBObject(db=db)


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections"""
    conn = get_connection()
    try:
        yield conn
    except:
        raise
    finally:
        conn.close()



def read_file_and_execute(file: str, conn: sqlite3.Connection) -> sqlite3.Cursor:
    with open(file) as f_obj:
        sql = f_obj.read()
    return conn.executescript(sql)

def db_initialize():
    conn = getDBObject()
    res = False
    try:
        read_file_and_execute(getSchemaPath(), conn)
        conn.commit()
        res = True
    except Exception:
        conn.rollback()
        res = False
    finally:
        conn.close()
    return res

def populate_default_values():
    conn = getDBObject()
    read_file_and_execute(getSymptomsPath(), conn)
    read_file_and_execute(getDiseasesPath(), conn)
    read_file_and_execute(getDiseasesSymptomRelationPath(), conn)
    read_file_and_execute(getEducationalContentPath(), conn)
    conn.commit()
    conn.close()


def reset_database(populate_default: bool = False):
    conn = getDBObject()
    read_file_and_execute(getResetSchemaPath(), conn)
    conn.commit()
    conn.close()
    db_initialize()
    if populate_default:
        populate_default_values()



