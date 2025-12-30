#!/bin/env python3

import os
import sqlite3

def getDBPath():
    """
    @returns the relative path of database file.
    """

    return ".\\database\\db.db"

def getDBPathAbs():
    """
    @returns the absolute path of database file. taken by @see getDBPath()
    """
    if not os.path.exists(getDBPath()):
        return None
    return os.path.abspath(getDBPath())

