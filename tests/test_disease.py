#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.disease import Disease, Diseases, DISEASE_SEVERITY_RANK, load_all_diseases, add_new_disease, set_disease_data, get_all_diseases_cache, get_severity_level_str


class TestDisease(unittest.TestCase):
    """Test the Disease entity class"""

    def setUp(self):
        self.disease = Disease(1, "Flu", "Viral", "high")

    def test_disease_init(self):
        """Test disease initialization"""
        self.assertEqual(self.disease.get_disease_id(), 1)
        self.assertEqual(self.disease.get_disease_name(), "Flu")
        self.assertEqual(self.disease.get_category(), "Viral")
        self.assertEqual(self.disease.get_severity_level(), 3)

    def test_disease_severity_levels(self):
        """Test different severity levels"""
        disease_low = Disease(2, "Common Cold", "Viral", "low")
        disease_med = Disease(3, "Pneumonia", "Bacterial", "medium")
        disease_high = Disease(4, "COVID-19", "Viral", "high")

        self.assertEqual(disease_low.get_severity_level(), 1)
        self.assertEqual(disease_med.get_severity_level(), 2)
        self.assertEqual(disease_high.get_severity_level(), 3)

    def test_disease_invalid_severity(self):
        """Test invalid severity level"""
        disease = Disease(5, "Unknown", "Unknown", "invalid")
        self.assertEqual(disease.get_severity_level(), 0)

    def test_disease_getters(self):
        """Test all disease getters"""
        self.assertEqual(self.disease.get_disease_id(), 1)
        self.assertEqual(self.disease.get_disease_name(), "Flu")
        self.assertEqual(self.disease.get_category(), "Viral")
        self.assertEqual(self.disease.get_severity_level(), 3)

    def test_disease_get_severity_level_str(self):
        """Test getting severity level as string"""
        self.assertEqual(self.disease.get_severity_level_str(), "high")
        disease_low = Disease(2, "Cold", "Viral", "low")
        self.assertEqual(disease_low.get_severity_level_str(), "low")

    def test_disease_invalid_severity_level_str(self):
        """Test getting string for invalid severity"""
        disease = Disease(5, "Unknown", "Unknown", "invalid")
        self.assertEqual(disease.get_severity_level_str(), "")

    def test_disease_update(self):
        """Test disease update"""
        self.disease.update("Updated Flu", "Viral", "low")
        self.assertEqual(self.disease.get_disease_name(), "Updated Flu")
        self.assertEqual(self.disease.get_severity_level(), 1)

    def test_disease_equality(self):
        """Test disease equality by ID"""
        disease2 = Disease(1, "Different Name", "Different Category", "low")
        disease3 = Disease(2, "Flu", "Viral", "high")
        self.assertEqual(self.disease, disease2)
        self.assertNotEqual(self.disease, disease3)

    def test_disease_hash(self):
        """Test disease hashing"""
        disease2 = Disease(1, "Different Name", "Different Category", "low")
        self.assertEqual(hash(self.disease), hash(disease2))

    def test_disease_equality_non_disease(self):
        """Test equality with non-Disease objects"""
        self.assertNotEqual(self.disease, "Not a disease")
        self.assertNotEqual(self.disease, 1)


class TestDiseases(unittest.TestCase):
    """Test the Diseases collection class"""

    def setUp(self):
        self.diseases = Diseases()
        self.disease1 = Disease(1, "Flu", "Viral", "high")
        self.disease2 = Disease(2, "Cold", "Viral", "low")
        self.disease3 = Disease(3, "Pneumonia", "Bacterial", "medium")

    def test_diseases_init(self):
        """Test diseases collection initialization"""
        self.assertEqual(len(self.diseases.get_all_diseases_list()), 0)

    def test_diseases_add(self):
        """Test adding diseases"""
        self.diseases.add(self.disease1)
        self.assertEqual(len(self.diseases.get_all_diseases_list()), 1)

    def test_diseases_add_duplicate(self):
        """Test that duplicate diseases are not added"""
        self.diseases.add(self.disease1)
        self.diseases.add(self.disease1)
        self.assertEqual(len(self.diseases.get_all_diseases_list()), 1)

    def test_diseases_add_none(self):
        """Test that None is not added"""
        self.diseases.add(None)
        self.assertEqual(len(self.diseases.get_all_diseases_list()), 0)

    def test_diseases_get_all_diseases_list(self):
        """Test getting all diseases"""
        self.diseases.add(self.disease1)
        self.diseases.add(self.disease2)
        all_diseases = self.diseases.get_all_diseases_list()
        self.assertEqual(len(all_diseases), 2)

    def test_diseases_len(self):
        """Test __len__ method"""
        self.diseases.add(self.disease1)
        self.diseases.add(self.disease2)
        self.assertEqual(len(self.diseases), 2)

    def test_diseases_iter(self):
        """Test iterating through diseases"""
        self.diseases.add(self.disease1)
        self.diseases.add(self.disease2)
        count = 0
        for disease in self.diseases:
            count += 1
        self.assertEqual(count, 2)

    def test_diseases_filter_by_id(self):
        """Test filtering diseases by ID"""
        self.diseases.add(self.disease1)
        self.diseases.add(self.disease2)
        filtered = self.diseases.filter_by_id(1)
        self.assertEqual(len(filtered.get_all_diseases_list()), 1)
        self.assertEqual(filtered.get_all_diseases_list()[0].get_disease_id(), 1)

    def test_diseases_filter_by_name(self):
        """Test filtering diseases by name"""
        self.diseases.add(self.disease1)
        self.diseases.add(self.disease2)
        filtered = self.diseases.filter_by_name("flu")
        self.assertEqual(len(filtered.get_all_diseases_list()), 1)

    def test_diseases_filter_by_category(self):
        """Test filtering diseases by category"""
        self.diseases.add(self.disease1)
        self.diseases.add(self.disease2)
        self.diseases.add(self.disease3)
        filtered = self.diseases.filter_by_category("Viral")
        self.assertEqual(len(filtered.get_all_diseases_list()), 2)

    def test_diseases_filter_by_severity(self):
        """Test filtering diseases by severity level"""
        self.diseases.add(self.disease1)
        self.diseases.add(self.disease2)
        self.diseases.add(self.disease3)
        filtered = self.diseases.filter_by_severity_level("high")
        self.assertEqual(len(filtered.get_all_diseases_list()), 1)


class TestDiseaseDatabase(unittest.TestCase):
    """Test disease database operations"""

    @patch('core.disease.coredb.getDBObject')
    def test_load_all_diseases(self, mock_get_db):
        """Test loading all diseases from database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "Flu", "Viral", "high"),
            (2, "Cold", "Viral", "low"),
            (3, "Pneumonia", "Bacterial", "medium")
        ]

        diseases = load_all_diseases()
        self.assertEqual(len(diseases.get_all_diseases_list()), 3)
        mock_conn.close.assert_called_once()

    @patch('core.disease.coredb.getDBObject')
    def test_load_all_diseases_empty(self, mock_get_db):
        """Test loading diseases when database is empty"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        diseases = load_all_diseases()
        self.assertEqual(len(diseases.get_all_diseases_list()), 0)

    @patch('core.disease.coredb.getDBObject')
    def test_load_all_diseases_exception(self, mock_get_db):
        """Test loading diseases with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            diseases = load_all_diseases()
        self.assertEqual(len(diseases.get_all_diseases_list()), 0)

    @patch('core.disease.coredb.getDBObject')
    def test_add_new_disease_success(self, mock_get_db):
        """Test adding a new disease"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        import core.disease
        core.disease.cache_all_diseases = None

        success, disease_id = add_new_disease("Flu", "Viral", "high")
        self.assertTrue(success)
        self.assertEqual(disease_id, 1)
        mock_conn.commit.assert_called_once()

    @patch('core.disease.coredb.getDBObject')
    def test_add_new_disease_with_int_severity(self, mock_get_db):
        """Test adding a disease with integer severity"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        import core.disease
        core.disease.cache_all_diseases = None

        success, disease_id = add_new_disease("Flu", "Viral", 3)
        self.assertTrue(success)

    @patch('core.disease.coredb.getDBObject')
    def test_add_new_disease_exception(self, mock_get_db):
        """Test adding a disease with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success, disease_id = add_new_disease("Flu", "Viral", "high")
        self.assertFalse(success)
        self.assertEqual(disease_id, -1)

    @patch('core.disease.coredb.getDBObject')
    def test_set_disease_data_success(self, mock_get_db):
        """Test updating disease data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        import core.disease
        core.disease.cache_all_diseases = None

        success = set_disease_data(1, "Updated Flu", "Viral", "low")
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('core.disease.coredb.getDBObject')
    def test_set_disease_data_exception(self, mock_get_db):
        """Test updating disease with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = set_disease_data(1, "Updated Flu", "Viral", "low")
        self.assertFalse(success)

    @patch('core.disease.load_all_diseases')
    def test_get_all_diseases_cache(self, mock_load):
        """Test getting diseases cache"""
        mock_diseases = Diseases()
        mock_diseases.add(Disease(1, "Flu", "Viral", "high"))
        mock_load.return_value = mock_diseases

        import core.disease
        core.disease.cache_all_diseases = None

        result = get_all_diseases_cache()
        self.assertEqual(len(result.get_all_diseases_list()), 1)

    @patch('core.disease.load_all_diseases')
    def test_get_all_diseases_cache_refresh(self, mock_load):
        """Test refreshing diseases cache"""
        mock_diseases = Diseases()
        mock_diseases.add(Disease(1, "Flu", "Viral", "high"))
        mock_load.return_value = mock_diseases

        import core.disease
        core.disease.cache_all_diseases = Diseases()

        result = get_all_diseases_cache(refresh_cache=True)
        mock_load.assert_called_once()

    def test_get_severity_level_str_low(self):
        """Test getting severity string for low level"""
        result = get_severity_level_str(1)
        self.assertEqual(result, "low")

    def test_get_severity_level_str_medium(self):
        """Test getting severity string for medium level"""
        result = get_severity_level_str(2)
        self.assertEqual(result, "medium")

    def test_get_severity_level_str_high(self):
        """Test getting severity string for high level"""
        result = get_severity_level_str(3)
        self.assertEqual(result, "high")

    def test_get_severity_level_str_invalid(self):
        """Test getting severity string for invalid level"""
        result = get_severity_level_str(999)
        self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()
