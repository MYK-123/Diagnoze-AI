#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.sessions import (
    create_session, validate_session, destroy_session,
    get_user_id_from_session
)


class TestSessions(unittest.TestCase):
    """Test session management functions"""

    @patch('auth.sessions.coredb.getDBObject')
    @patch('auth.sessions.uuid.uuid4')
    def test_create_session_success(self, mock_uuid, mock_get_db):
        """Test creating a session"""
        mock_uuid.return_value = "test-uuid-token"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        session_token = create_session(1)
        self.assertEqual(session_token, "test-uuid-token")
        mock_conn.commit.assert_called_once()

    @patch('auth.sessions.coredb.getDBObject')
    @patch('auth.sessions.uuid.uuid4')
    def test_create_session_exception(self, mock_uuid, mock_get_db):
        """Test creating session with database exception"""
        mock_uuid.return_value = "test-uuid-token"
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            session_token = create_session(1)
        self.assertEqual(session_token, "test-uuid-token")
        mock_conn.rollback.assert_called_once()

    @patch('auth.sessions.coredb.getDBObject')
    def test_validate_session_valid(self, mock_get_db):
        """Test validating a valid session"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)

        is_valid = validate_session("test-token", 1)
        self.assertTrue(is_valid)

    @patch('auth.sessions.coredb.getDBObject')
    def test_validate_session_invalid(self, mock_get_db):
        """Test validating an invalid session"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (0,)

        is_valid = validate_session("test-token", 1)
        self.assertFalse(is_valid)

    @patch('auth.sessions.coredb.getDBObject')
    def test_validate_session_exception(self, mock_get_db):
        """Test validating session with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            is_valid = validate_session("test-token", 1)
        self.assertFalse(is_valid)

    @patch('auth.sessions.coredb.getDBObject')
    def test_destroy_session_success(self, mock_get_db):
        """Test destroying a session"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        success = destroy_session("test-token")
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('auth.sessions.coredb.getDBObject')
    def test_destroy_session_exception(self, mock_get_db):
        """Test destroying session with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = destroy_session("test-token")
        self.assertFalse(success)
        mock_conn.rollback.assert_called_once()

    @patch('auth.sessions.coredb.getDBObject')
    def test_get_user_id_from_session_found(self, mock_get_db):
        """Test getting user ID from valid session"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)

        user_id = get_user_id_from_session("test-token")
        self.assertEqual(user_id, 1)

    @patch('auth.sessions.coredb.getDBObject')
    def test_get_user_id_from_session_not_found(self, mock_get_db):
        """Test getting user ID from invalid session"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        user_id = get_user_id_from_session("invalid-token")
        self.assertIsNone(user_id)

    @patch('auth.sessions.coredb.getDBObject')
    def test_get_user_id_from_session_exception(self, mock_get_db):
        """Test getting user ID with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            user_id = get_user_id_from_session("test-token")
        self.assertIsNone(user_id)


if __name__ == '__main__':
    unittest.main()
