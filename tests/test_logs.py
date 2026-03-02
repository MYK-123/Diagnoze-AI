#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logs import Log, get_all_logs, add_new_log


class TestLog(unittest.TestCase):
    """Test the Log entity class"""

    def setUp(self):
        self.log = Log(1, 1, "login", "2024-01-01 10:00:00")

    def test_log_init(self):
        """Test log initialization"""
        self.assertEqual(self.log.log_id, 1)
        self.assertEqual(self.log.user_id, 1)
        self.assertEqual(self.log.action_type, "login")
        self.assertEqual(self.log.created_at, "2024-01-01 10:00:00")

    def test_log_attributes(self):
        """Test all log attributes"""
        self.assertEqual(self.log.log_id, 1)
        self.assertEqual(self.log.user_id, 1)
        self.assertEqual(self.log.action_type, "login")
        self.assertEqual(self.log.created_at, "2024-01-01 10:00:00")

    def test_log_different_actions(self):
        """Test log with different action types"""
        log_logout = Log(2, 1, "logout", "2024-01-01 11:00:00")
        log_predict = Log(3, 2, "predict", "2024-01-01 12:00:00")

        self.assertEqual(log_logout.action_type, "logout")
        self.assertEqual(log_predict.action_type, "predict")


class TestLogsDatabase(unittest.TestCase):
    """Test logs database operations"""

    @patch('core.logs.coredb.getDBObject')
    def test_get_all_logs_success(self, mock_get_db):
        """Test getting all logs from database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 1, "login", "2024-01-01 10:00:00"),
            (2, 1, "logout", "2024-01-01 11:00:00"),
            (3, 2, "predict", "2024-01-01 12:00:00")
        ]

        logs = get_all_logs()
        self.assertEqual(len(logs), 3)
        self.assertEqual(logs[0].action_type, "login")
        self.assertEqual(logs[1].action_type, "logout")
        self.assertEqual(logs[2].action_type, "predict")
        mock_conn.close.assert_called()

    @patch('core.logs.coredb.getDBObject')
    def test_get_all_logs_empty(self, mock_get_db):
        """Test getting logs when database is empty"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        logs = get_all_logs()
        self.assertEqual(len(logs), 0)

    @patch('core.logs.coredb.getDBObject')
    def test_get_all_logs_exception(self, mock_get_db):
        """Test getting logs with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            logs = get_all_logs()
        self.assertEqual(len(logs), 0)

    @patch('core.logs.coredb.getDBObject')
    def test_add_new_log_success(self, mock_get_db):
        """Test adding a new log"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        success = add_new_log(1, "login")
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('core.logs.coredb.getDBObject')
    def test_add_new_log_exception(self, mock_get_db):
        """Test adding log with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = add_new_log(1, "login")
        self.assertFalse(success)
        mock_conn.rollback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
