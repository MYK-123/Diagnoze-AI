#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from content.educational_content import (
    EducationContent, EducationContents,
    load_all_education_content, add_new_educational_content,
    set_educational_content_verification, get_all_education_content_cache
)


class TestEducationContent(unittest.TestCase):
    """Test the EducationContent entity class"""

    def setUp(self):
        self.content = EducationContent(1, 1, "Flu Overview", "Flu is a viral infection...", True)

    def test_education_content_init(self):
        """Test education content initialization"""
        self.assertEqual(self.content.get_content_id(), 1)
        self.assertEqual(self.content.get_disease_id(), 1)
        self.assertEqual(self.content.get_title(), "Flu Overview")
        self.assertEqual(self.content.get_content_text(), "Flu is a viral infection...")
        self.assertTrue(self.content.get_is_verified())

    def test_education_content_getters(self):
        """Test all education content getters"""
        self.assertEqual(self.content.get_content_id(), 1)
        self.assertEqual(self.content.get_disease_id(), 1)
        self.assertEqual(self.content.get_title(), "Flu Overview")
        self.assertEqual(self.content.get_content_text(), "Flu is a viral infection...")
        self.assertTrue(self.content.get_is_verified())

    def test_education_content_set_verification(self):
        """Test setting verification status"""
        self.content.set_verification(False)
        self.assertFalse(self.content.get_is_verified())
        self.content.set_verification(True)
        self.assertTrue(self.content.get_is_verified())

    def test_education_content_equality(self):
        """Test education content equality by ID"""
        content2 = EducationContent(1, 2, "Different Title", "Different text", False)
        content3 = EducationContent(2, 1, "Flu Overview", "Flu is a viral infection...", True)
        self.assertEqual(self.content, content2)
        self.assertNotEqual(self.content, content3)

    def test_education_content_hash(self):
        """Test education content hashing"""
        content2 = EducationContent(1, 2, "Different Title", "Different text", False)
        self.assertEqual(hash(self.content), hash(content2))

    def test_education_content_equality_non_content(self):
        """Test equality with non-EducationContent objects"""
        self.assertNotEqual(self.content, "Not content")
        self.assertNotEqual(self.content, 1)


class TestEducationContents(unittest.TestCase):
    """Test the EducationContents collection class"""

    def setUp(self):
        self.contents = EducationContents()
        self.content1 = EducationContent(1, 1, "Flu Overview", "Text about flu", True)
        self.content2 = EducationContent(2, 2, "Cold Overview", "Text about cold", False)
        self.content3 = EducationContent(3, 1, "Flu Treatment", "Treatment text", True)

    def test_education_contents_init(self):
        """Test education contents collection initialization"""
        self.assertEqual(len(self.contents.get_all_list()), 0)

    def test_education_contents_add(self):
        """Test adding education contents"""
        self.contents.add(self.content1)
        self.assertEqual(len(self.contents.get_all_list()), 1)

    def test_education_contents_add_duplicate(self):
        """Test that duplicate contents are not added"""
        self.contents.add(self.content1)
        self.contents.add(self.content1)
        self.assertEqual(len(self.contents.get_all_list()), 1)

    def test_education_contents_add_none(self):
        """Test that None is not added"""
        self.contents.add(None)
        self.assertEqual(len(self.contents.get_all_list()), 0)

    def test_education_contents_iter(self):
        """Test iterating through contents"""
        self.contents.add(self.content1)
        self.contents.add(self.content2)
        count = 0
        for content in self.contents:
            count += 1
        self.assertEqual(count, 2)

    def test_education_contents_filter_by_content_id(self):
        """Test filtering contents by content ID"""
        self.contents.add(self.content1)
        self.contents.add(self.content2)
        filtered = self.contents.filter_by_content_id(1)
        self.assertEqual(len(filtered.get_all_list()), 1)

    def test_education_contents_filter_by_disease_id(self):
        """Test filtering contents by disease ID"""
        self.contents.add(self.content1)
        self.contents.add(self.content2)
        self.contents.add(self.content3)
        filtered = self.contents.filter_by_disease_id(1)
        self.assertEqual(len(filtered.get_all_list()), 2)

    def test_education_contents_filter_by_title(self):
        """Test filtering contents by title"""
        self.contents.add(self.content1)
        self.contents.add(self.content2)
        filtered = self.contents.filter_by_title("overview")
        self.assertEqual(len(filtered.get_all_list()), 2)


class TestEducationContentDatabase(unittest.TestCase):
    """Test education content database operations"""

    @patch('content.educational_content.coredb.getDBObject')
    def test_load_all_education_content(self, mock_get_db):
        """Test loading all education content from database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 1, "Flu Overview", "Text about flu", 1),
            (2, 2, "Cold Overview", "Text about cold", 0),
            (3, 1, "Flu Treatment", "Treatment text", 1)
        ]

        contents = load_all_education_content()
        self.assertEqual(len(contents.get_all_list()), 3)
        mock_conn.close.assert_called_once()

    @patch('content.educational_content.coredb.getDBObject')
    def test_load_all_education_content_empty(self, mock_get_db):
        """Test loading content when database is empty"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        contents = load_all_education_content()
        self.assertEqual(len(contents.get_all_list()), 0)

    @patch('content.educational_content.coredb.getDBObject')
    def test_load_all_education_content_exception(self, mock_get_db):
        """Test loading content with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            contents = load_all_education_content()
        self.assertEqual(len(contents.get_all_list()), 0)

    @patch('content.educational_content.coredb.getDBObject')
    def test_add_new_educational_content_success(self, mock_get_db):
        """Test adding new educational content"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        import content.educational_content
        content.educational_content.cache_all_education_content = None

        success = add_new_educational_content(1, "Flu Overview", "Text", True)
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('content.educational_content.coredb.getDBObject')
    def test_add_new_educational_content_exception(self, mock_get_db):
        """Test adding content with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = add_new_educational_content(1, "Flu Overview", "Text", True)
        self.assertFalse(success)

    @patch('content.educational_content.coredb.getDBObject')
    def test_set_educational_content_verification_success(self, mock_get_db):
        """Test updating content verification"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        import content.educational_content
        content.educational_content.cache_all_education_content = None

        success = set_educational_content_verification(1, False)
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('content.educational_content.coredb.getDBObject')
    def test_set_educational_content_verification_exception(self, mock_get_db):
        """Test updating verification with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = set_educational_content_verification(1, False)
        self.assertFalse(success)

    @patch('content.educational_content.load_all_education_content')
    def test_get_all_education_content_cache(self, mock_load):
        """Test getting education content cache"""
        mock_contents = EducationContents()
        mock_contents.add(EducationContent(1, 1, "Flu Overview", "Text", True))
        mock_load.return_value = mock_contents

        import content.educational_content
        content.educational_content.cache_all_education_content = None

        result = get_all_education_content_cache()
        self.assertEqual(len(result.get_all_list()), 1)


if __name__ == '__main__':
    unittest.main()
