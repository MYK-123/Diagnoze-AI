#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.extracted_symptoms import (
    SymptomExtracted, SymptomExtracteds,
    load_all_symptom_extracted, add_new_symptom_extracted,
    set_symptom_extracted_data, get_all_symptom_extracted_cache
)


class TestSymptomExtracted(unittest.TestCase):
    """Test the SymptomExtracted entity class"""

    def setUp(self):
        self.extracted = SymptomExtracted(1, 1, 2, 0.95)

    def test_symptom_extracted_init(self):
        """Test symptom extracted initialization"""
        self.assertEqual(self.extracted.get_extracted_id(), 1)
        self.assertEqual(self.extracted.get_input_id(), 1)
        self.assertEqual(self.extracted.get_symptom_id(), 2)
        self.assertEqual(self.extracted.get_confidence_score(), 0.95)

    def test_symptom_extracted_getters(self):
        """Test all symptom extracted getters"""
        self.assertEqual(self.extracted.get_extracted_id(), 1)
        self.assertEqual(self.extracted.get_input_id(), 1)
        self.assertEqual(self.extracted.get_symptom_id(), 2)
        self.assertEqual(self.extracted.get_confidence_score(), 0.95)

    def test_symptom_extracted_update(self):
        """Test symptom extracted update"""
        self.extracted.update(2, 3, 0.85)
        self.assertEqual(self.extracted.get_input_id(), 2)
        self.assertEqual(self.extracted.get_symptom_id(), 3)
        self.assertEqual(self.extracted.get_confidence_score(), 0.85)

    def test_symptom_extracted_equality(self):
        """Test symptom extracted equality by ID"""
        extracted2 = SymptomExtracted(1, 5, 6, 0.5)
        extracted3 = SymptomExtracted(2, 1, 2, 0.95)
        self.assertEqual(self.extracted, extracted2)
        self.assertNotEqual(self.extracted, extracted3)

    def test_symptom_extracted_hash(self):
        """Test symptom extracted hashing"""
        extracted2 = SymptomExtracted(1, 5, 6, 0.5)
        self.assertEqual(hash(self.extracted), hash(extracted2))

    def test_symptom_extracted_equality_non_extracted(self):
        """Test equality with non-SymptomExtracted objects"""
        self.assertNotEqual(self.extracted, "Not extracted")
        self.assertNotEqual(self.extracted, 1)


class TestSymptomExtracteds(unittest.TestCase):
    """Test the SymptomExtracteds collection class"""

    def setUp(self):
        self.extracteds = SymptomExtracteds()
        self.ext1 = SymptomExtracted(1, 1, 2, 0.95)
        self.ext2 = SymptomExtracted(2, 1, 3, 0.70)
        self.ext3 = SymptomExtracted(3, 2, 2, 0.88)

    def test_symptom_extracteds_init(self):
        """Test symptom extracteds collection initialization"""
        self.assertEqual(len(self.extracteds.get_all_list()), 0)

    def test_symptom_extracteds_add(self):
        """Test adding symptom extracteds"""
        self.extracteds.add(self.ext1)
        self.assertEqual(len(self.extracteds.get_all_list()), 1)

    def test_symptom_extracteds_add_duplicate(self):
        """Test that duplicate extracteds are not added"""
        self.extracteds.add(self.ext1)
        self.extracteds.add(self.ext1)
        self.assertEqual(len(self.extracteds.get_all_list()), 1)

    def test_symptom_extracteds_add_none(self):
        """Test that None is not added"""
        self.extracteds.add(None)
        self.assertEqual(len(self.extracteds.get_all_list()), 0)

    def test_symptom_extracteds_filter_by_extracted_id(self):
        """Test filtering by extracted ID"""
        self.extracteds.add(self.ext1)
        self.extracteds.add(self.ext2)
        filtered = self.extracteds.filter_by_extracted_id(1)
        self.assertEqual(len(filtered.get_all_list()), 1)

    def test_symptom_extracteds_filter_by_input_id(self):
        """Test filtering by input ID"""
        self.extracteds.add(self.ext1)
        self.extracteds.add(self.ext2)
        self.extracteds.add(self.ext3)
        filtered = self.extracteds.filter_by_input_id(1)
        self.assertEqual(len(filtered.get_all_list()), 2)

    def test_symptom_extracteds_filter_by_symptom_id(self):
        """Test filtering by symptom ID"""
        self.extracteds.add(self.ext1)
        self.extracteds.add(self.ext2)
        self.extracteds.add(self.ext3)
        filtered = self.extracteds.filter_by_symptom_id(2)
        self.assertEqual(len(filtered.get_all_list()), 2)

    def test_symptom_extracteds_filter_by_confidence_score(self):
        """Test filtering by exact confidence score"""
        self.extracteds.add(self.ext1)
        self.extracteds.add(self.ext2)
        filtered = self.extracteds.filter_by_confidence_score(0.95)
        self.assertEqual(len(filtered.get_all_list()), 1)

    def test_symptom_extracteds_filter_by_confidence_min(self):
        """Test filtering by minimum confidence score"""
        self.extracteds.add(self.ext1)
        self.extracteds.add(self.ext2)
        self.extracteds.add(self.ext3)
        filtered = self.extracteds.filter_by_confidence_min(0.85)
        self.assertEqual(len(filtered.get_all_list()), 2)

    def test_symptom_extracteds_filter_by_confidence_max(self):
        """Test filtering by maximum confidence score"""
        self.extracteds.add(self.ext1)
        self.extracteds.add(self.ext2)
        self.extracteds.add(self.ext3)
        filtered = self.extracteds.filter_by_confidence_max(0.85)
        self.assertEqual(len(filtered.get_all_list()), 1)

    def test_symptom_extracteds_filter_by_confidence_range(self):
        """Test filtering by confidence range"""
        self.extracteds.add(self.ext1)
        self.extracteds.add(self.ext2)
        self.extracteds.add(self.ext3)
        filtered = self.extracteds.filter_by_confidence_range(0.75, 0.92)
        self.assertEqual(len(filtered.get_all_list()), 1)


class TestSymptomExtractedsDatabase(unittest.TestCase):
    """Test symptom extracteds database operations"""

    @patch('core.extracted_symptoms.coredb.getDBObject')
    def test_load_all_symptom_extracted(self, mock_get_db):
        """Test loading all symptom extracted from database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 1, 2, 0.95),
            (2, 1, 3, 0.70),
            (3, 2, 2, 0.88)
        ]

        extracteds = load_all_symptom_extracted()
        self.assertEqual(len(extracteds.get_all_list()), 3)
        mock_conn.close.assert_called_once()

    @patch('core.extracted_symptoms.coredb.getDBObject')
    def test_load_all_symptom_extracted_empty(self, mock_get_db):
        """Test loading extracteds when database is empty"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        extracteds = load_all_symptom_extracted()
        self.assertEqual(len(extracteds.get_all_list()), 0)

    @patch('core.extracted_symptoms.coredb.getDBObject')
    def test_load_all_symptom_extracted_exception(self, mock_get_db):
        """Test loading extracteds with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            extracteds = load_all_symptom_extracted()
        self.assertEqual(len(extracteds.get_all_list()), 0)

    @patch('core.extracted_symptoms.coredb.getDBObject')
    def test_add_new_symptom_extracted_success(self, mock_get_db):
        """Test adding a new symptom extracted"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        import core.extracted_symptoms
        core.extracted_symptoms.cache_all_symptom_extracted = None

        success = add_new_symptom_extracted(1, 2, 0.95)
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('core.extracted_symptoms.coredb.getDBObject')
    def test_add_new_symptom_extracted_exception(self, mock_get_db):
        """Test adding a symptom extracted with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = add_new_symptom_extracted(1, 2, 0.95)
        self.assertFalse(success)

    @patch('core.extracted_symptoms.coredb.getDBObject')
    def test_set_symptom_extracted_data_success(self, mock_get_db):
        """Test updating symptom extracted data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        import core.extracted_symptoms
        core.extracted_symptoms.cache_all_symptom_extracted = None

        success = set_symptom_extracted_data(1, 2, 3, 0.85)
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('core.extracted_symptoms.coredb.getDBObject')
    def test_set_symptom_extracted_data_exception(self, mock_get_db):
        """Test updating symptom extracted with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = set_symptom_extracted_data(1, 2, 3, 0.85)
        self.assertFalse(success)

    @patch('core.extracted_symptoms.load_all_symptom_extracted')
    def test_get_all_symptom_extracted_cache(self, mock_load):
        """Test getting symptom extracted cache"""
        mock_extracteds = SymptomExtracteds()
        mock_extracteds.add(SymptomExtracted(1, 1, 2, 0.95))
        mock_load.return_value = mock_extracteds

        import core.extracted_symptoms
        core.extracted_symptoms.cache_all_symptom_extracted = None

        result = get_all_symptom_extracted_cache()
        self.assertEqual(len(result.get_all_list()), 1)


if __name__ == '__main__':
    unittest.main()
