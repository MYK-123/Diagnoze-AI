#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.core import (
    getDBPath, getSchemaPath, getResetSchemaPath,
    getSymptomsPath, getDiseasesPath, getDiseasesSymptomRelationPath,
    getEducationalContentPath, getDBPathAbs, getDBObject,
    read_file_and_execute, db_initialize, populate_default_values,
    reset_database
)


class TestDatabasePaths(unittest.TestCase):
    """Test database path functions"""

    def test_get_db_path(self):
        """Test getting database path"""
        path = getDBPath()
        self.assertIsNotNone(path)
        self.assertIn("db.db", path)

    def test_get_schema_path(self):
        """Test getting schema path"""
        path = getSchemaPath()
        self.assertIsNotNone(path)
        self.assertIn("schema.sql", path)

    def test_get_reset_schema_path(self):
        """Test getting reset schema path"""
        path = getResetSchemaPath()
        self.assertIsNotNone(path)
        self.assertIn("reset_db.sql", path)

    def test_get_symptoms_path(self):
        """Test getting symptoms path"""
        path = getSymptomsPath()
        self.assertIsNotNone(path)
        self.assertIn("symptoms.sql", path)

    def test_get_diseases_path(self):
        """Test getting diseases path"""
        path = getDiseasesPath()
        self.assertIsNotNone(path)
        self.assertIn("disease.sql", path)

    def test_get_diseases_symptom_relation_path(self):
        """Test getting disease-symptom relation path"""
        path = getDiseasesSymptomRelationPath()
        self.assertIsNotNone(path)
        self.assertIn("disease_symptoms.sql", path)

    def test_get_educational_content_path(self):
        """Test getting educational content path"""
        path = getEducationalContentPath()
        self.assertIsNotNone(path)
        self.assertIn("educational_content.sql", path)


class TestDatabaseConnection(unittest.TestCase):
    """Test database connection functions"""

    @patch('db.core.os.path.exists')
    def test_get_db_path_abs_exists(self, mock_exists):
        """Test getting absolute DB path when file exists"""
        mock_exists.return_value = True
        
        with patch('db.core.os.path.abspath') as mock_abspath:
            mock_abspath.return_value = "/absolute/path/db.db"
            path = getDBPathAbs()
            self.assertEqual(path, "/absolute/path/db.db")

    @patch('db.core.os.path.exists')
    def test_get_db_path_abs_not_exists(self, mock_exists):
        """Test getting absolute DB path when file doesn't exist"""
        mock_exists.return_value = False
        
        path = getDBPathAbs()
        self.assertIsNone(path)

    @patch('db.core.sqlite3.connect')
    def test_get_db_object_default(self, mock_connect):
        """Test getting database object with default path"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        conn = getDBObject()
        self.assertIsNotNone(conn)

    @patch('db.core.sqlite3.connect')
    def test_get_db_object_custom(self, mock_connect):
        """Test getting database object with custom path"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        conn = getDBObject(":memory:")
        self.assertIsNotNone(conn)
        mock_connect.assert_called_with(":memory:")


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations"""

    def test_read_file_and_execute(self):
        """Test reading and executing SQL file"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.executescript.return_value = mock_cursor
        
        sql_content = "CREATE TABLE test (id INTEGER);"
        
        with patch('builtins.open', mock_open(read_data=sql_content)):
            result = read_file_and_execute("test.sql", mock_conn)
            self.assertIsNotNone(result)
            mock_conn.executescript.assert_called_once()

    @patch('db.core.populate_default_values')
    @patch('db.core.read_file_and_execute')
    @patch('db.core.getDBObject')
    def test_db_initialize(self, mock_get_db, mock_read_file, mock_populate):
        """Test database initialization"""
        mock_conn = MagicMock()
        mock_get_db.return_value = mock_conn
        
        db_initialize()
        
        mock_read_file.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('db.core.populate_default_values')
    @patch('db.core.db_initialize')
    @patch('db.core.read_file_and_execute')
    @patch('db.core.getDBObject')
    def test_reset_database_with_populate(self, mock_get_db, mock_read_file, mock_db_init, mock_populate):
        """Test resetting database with default values"""
        mock_conn = MagicMock()
        mock_get_db.return_value = mock_conn
        
        reset_database(populate_default=True)
        
        self.assertEqual(mock_read_file.call_count, 1)
        mock_conn.commit.assert_called()
        mock_populate.assert_called_once()

    @patch('db.core.db_initialize')
    @patch('db.core.read_file_and_execute')
    @patch('db.core.getDBObject')
    def test_reset_database_without_populate(self, mock_get_db, mock_read_file, mock_db_init):
        """Test resetting database without default values"""
        mock_conn = MagicMock()
        mock_get_db.return_value = mock_conn
        
        reset_database(populate_default=False)
        
        mock_db_init.assert_called_once()
        mock_conn.close.assert_called()

    @patch('db.core.read_file_and_execute')
    @patch('db.core.getDBObject')
    def test_populate_default_values(self, mock_get_db, mock_read_file):
        """Test populating default values"""
        mock_conn = MagicMock()
        mock_get_db.return_value = mock_conn
        
        populate_default_values()
        
        # Should call read_file_and_execute 4 times (symptoms, diseases, relations, educational_content)
        self.assertEqual(mock_read_file.call_count, 4)
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
