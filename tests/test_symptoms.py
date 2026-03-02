#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.symptoms import Symptom, Symptoms, load_all_symptoms, add_new_symptom, set_symptom_data, get_all_symptoms_cache


class TestSymptom(unittest.TestCase):
    """Test the Symptom entity class"""

    def setUp(self):
        self.symptom = Symptom(1, "Headache", "Pain")

    def test_symptom_init(self):
        """Test symptom initialization"""
        self.assertEqual(self.symptom.get_id(), 1)
        self.assertEqual(self.symptom.get_name(), "Headache")
        self.assertEqual(self.symptom.get_category(), "Pain")

    def test_symptom_getters(self):
        """Test all symptom getters"""
        self.assertEqual(self.symptom.get_id(), 1)
        self.assertEqual(self.symptom.get_name(), "Headache")
        self.assertEqual(self.symptom.get_category(), "Pain")

    def test_symptom_update(self):
        """Test symptom update"""
        self.symptom.update("Fever", "Temperature")
        self.assertEqual(self.symptom.get_name(), "Fever")
        self.assertEqual(self.symptom.get_category(), "Temperature")

    def test_symptom_equality(self):
        """Test symptom equality by ID"""
        symptom2 = Symptom(1, "Different Name", "Different Category")
        symptom3 = Symptom(2, "Headache", "Pain")
        self.assertEqual(self.symptom, symptom2)
        self.assertNotEqual(self.symptom, symptom3)

    def test_symptom_hash(self):
        """Test symptom hashing"""
        symptom2 = Symptom(1, "Different Name", "Different Category")
        self.assertEqual(hash(self.symptom), hash(symptom2))

    def test_symptom_equality_non_symptom(self):
        """Test equality with non-Symptom objects"""
        self.assertNotEqual(self.symptom, "Not a symptom")
        self.assertNotEqual(self.symptom, 1)
        self.assertNotEqual(self.symptom, None)


class TestSymptoms(unittest.TestCase):
    """Test the Symptoms collection class"""

    def setUp(self):
        self.symptoms = Symptoms()
        self.symptom1 = Symptom(1, "Headache", "Pain")
        self.symptom2 = Symptom(2, "Fever", "Temperature")
        self.symptom3 = Symptom(3, "Cough", "Respiratory")

    def test_symptoms_init(self):
        """Test symptoms collection initialization"""
        self.assertEqual(len(self.symptoms.get_all_list()), 0)

    def test_symptoms_add(self):
        """Test adding symptoms"""
        self.symptoms.add(self.symptom1)
        self.assertEqual(len(self.symptoms.get_all_list()), 1)
        self.assertIn(self.symptom1, self.symptoms.get_all_list())

    def test_symptoms_add_duplicate(self):
        """Test that duplicate symptoms are not added"""
        self.symptoms.add(self.symptom1)
        self.symptoms.add(self.symptom1)
        self.assertEqual(len(self.symptoms.get_all_list()), 1)

    def test_symptoms_add_none(self):
        """Test that None is not added"""
        self.symptoms.add(None)
        self.assertEqual(len(self.symptoms.get_all_list()), 0)

    def test_symptoms_get_all_list(self):
        """Test getting all symptoms"""
        self.symptoms.add(self.symptom1)
        self.symptoms.add(self.symptom2)
        all_symptoms = self.symptoms.get_all_list()
        self.assertEqual(len(all_symptoms), 2)
        self.assertIn(self.symptom1, all_symptoms)
        self.assertIn(self.symptom2, all_symptoms)

    def test_symptoms_filter_by_id(self):
        """Test filtering symptoms by ID"""
        self.symptoms.add(self.symptom1)
        self.symptoms.add(self.symptom2)
        filtered = self.symptoms.filter_by_id(1)
        self.assertEqual(len(filtered.get_all_list()), 1)
        self.assertEqual(filtered.get_all_list()[0].get_id(), 1)

    def test_symptoms_filter_by_name(self):
        """Test filtering symptoms by name"""
        self.symptoms.add(self.symptom1)
        self.symptoms.add(self.symptom2)
        filtered = self.symptoms.filter_by_name("head")
        self.assertEqual(len(filtered.get_all_list()), 1)
        self.assertEqual(filtered.get_all_list()[0].get_name(), "Headache")

    def test_symptoms_filter_by_category(self):
        """Test filtering symptoms by category"""
        self.symptoms.add(self.symptom1)
        self.symptoms.add(self.symptom2)
        self.symptoms.add(self.symptom3)
        filtered = self.symptoms.filter_by_category("Pain")
        self.assertEqual(len(filtered.get_all_list()), 1)
        self.assertEqual(filtered.get_all_list()[0].get_category(), "Pain")

    def test_symptoms_filter_case_insensitive(self):
        """Test that filtering is case insensitive"""
        self.symptoms.add(self.symptom1)
        filtered_name = self.symptoms.filter_by_name("HEADACHE")
        self.assertEqual(len(filtered_name.get_all_list()), 1)
        filtered_cat = self.symptoms.filter_by_category("pain")
        self.assertEqual(len(filtered_cat.get_all_list()), 1)

    def test_symptoms_iter(self):
        """Test iterating through symptoms"""
        self.symptoms.add(self.symptom1)
        self.symptoms.add(self.symptom2)
        count = 0
        for symptom in self.symptoms:
            count += 1
        self.assertEqual(count, 2)


class TestSymptomsDatabase(unittest.TestCase):
    """Test symptoms database operations"""

    @patch('core.symptoms.coredb.getDBObject')
    def test_load_all_symptoms(self, mock_get_db):
        """Test loading all symptoms from database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "Headache", "Pain"),
            (2, "Fever", "Temperature"),
            (3, "Cough", "Respiratory")
        ]

        symptoms = load_all_symptoms()
        self.assertEqual(len(symptoms.get_all_list()), 3)
        mock_conn.close.assert_called_once()

    @patch('core.symptoms.coredb.getDBObject')
    def test_load_all_symptoms_empty(self, mock_get_db):
        """Test loading symptoms when database is empty"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        symptoms = load_all_symptoms()
        self.assertEqual(len(symptoms.get_all_list()), 0)

    @patch('core.symptoms.coredb.getDBObject')
    def test_load_all_symptoms_exception(self, mock_get_db):
        """Test loading symptoms with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            symptoms = load_all_symptoms()
        self.assertEqual(len(symptoms.get_all_list()), 0)

    @patch('core.symptoms.coredb.getDBObject')
    @patch('core.symptoms.load_all_symptoms')
    def test_add_new_symptom_success(self, mock_load, mock_get_db):
        """Test adding a new symptom"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        # Reset cache
        import core.symptoms
        core.symptoms.cache_all_symptoms = None

        success, symptom_id = add_new_symptom("Headache", "Pain")
        self.assertTrue(success)
        self.assertEqual(symptom_id, 1)
        mock_conn.commit.assert_called_once()

    @patch('core.symptoms.coredb.getDBObject')
    def test_add_new_symptom_exception(self, mock_get_db):
        """Test adding a symptom with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success, symptom_id = add_new_symptom("Headache", "Pain")
        self.assertFalse(success)
        self.assertEqual(symptom_id, -1)
        mock_conn.rollback.assert_called_once()

    @patch('core.symptoms.coredb.getDBObject')
    def test_set_symptom_data_success(self, mock_get_db):
        """Test updating symptom data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        import core.symptoms
        core.symptoms.cache_all_symptoms = None

        success = set_symptom_data(1, "Updated Name", "Updated Category")
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('core.symptoms.coredb.getDBObject')
    def test_set_symptom_data_exception(self, mock_get_db):
        """Test updating symptom with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = set_symptom_data(1, "Updated Name", "Updated Category")
        self.assertFalse(success)
        mock_conn.rollback.assert_called_once()

    @patch('core.symptoms.load_all_symptoms')
    def test_get_all_symptoms_cache(self, mock_load):
        """Test getting symptoms cache"""
        mock_symptoms = Symptoms()
        mock_symptoms.add(Symptom(1, "Headache", "Pain"))
        mock_load.return_value = mock_symptoms

        import core.symptoms
        core.symptoms.cache_all_symptoms = None

        result = get_all_symptoms_cache()
        self.assertEqual(len(result.get_all_list()), 1)

    @patch('core.symptoms.load_all_symptoms')
    def test_get_all_symptoms_cache_refresh(self, mock_load):
        """Test refreshing symptoms cache"""
        mock_symptoms = Symptoms()
        mock_symptoms.add(Symptom(1, "Headache", "Pain"))
        mock_load.return_value = mock_symptoms

        import core.symptoms
        core.symptoms.cache_all_symptoms = Symptoms()

        result = get_all_symptoms_cache(refresh_cache=True)
        mock_load.assert_called_once()


if __name__ == '__main__':
    unittest.main()
