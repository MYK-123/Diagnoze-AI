#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.symptoms_input import (
    SymptomInput, SymptomInputs,
    load_all_symptom_inputs, add_new_symptom_input,
    set_symptom_input_data, get_all_symptom_inputs_cache
)


class TestSymptomInput(unittest.TestCase):
    """Test the SymptomInput entity class"""

    def setUp(self):
        self.input = SymptomInput(1, "1", "I have a headache", "2024-01-01")

    def test_symptom_input_init(self):
        """Test symptom input initialization"""
        self.assertEqual(self.input.get_input_id(), 1)
        self.assertEqual(self.input.get_user_id(), "1")
        self.assertEqual(self.input.get_input_text(), "I have a headache")
        self.assertEqual(self.input.get_created_at(), "2024-01-01")

    def test_symptom_input_getters(self):
        """Test all symptom input getters"""
        self.assertEqual(self.input.get_input_id(), 1)
        self.assertEqual(self.input.get_user_id(), "1")
        self.assertEqual(self.input.get_input_text(), "I have a headache")
        self.assertEqual(self.input.get_created_at(), "2024-01-01")

    def test_symptom_input_update(self):
        """Test symptom input update"""
        self.input.update("2", "I have a fever", "2024-01-02")
        self.assertEqual(self.input.get_user_id(), "2")
        self.assertEqual(self.input.get_input_text(), "I have a fever")
        self.assertEqual(self.input.get_created_at(), "2024-01-02")

    def test_symptom_input_equality(self):
        """Test symptom input equality by ID"""
        input2 = SymptomInput(1, "2", "Different text", "2024-01-02")
        input3 = SymptomInput(2, "1", "I have a headache", "2024-01-01")
        self.assertEqual(self.input, input2)
        self.assertNotEqual(self.input, input3)

    def test_symptom_input_hash(self):
        """Test symptom input hashing"""
        input2 = SymptomInput(1, "2", "Different text", "2024-01-02")
        self.assertEqual(hash(self.input), hash(input2))

    def test_symptom_input_equality_non_input(self):
        """Test equality with non-SymptomInput objects"""
        self.assertNotEqual(self.input, "Not an input")
        self.assertNotEqual(self.input, 1)


class TestSymptomInputs(unittest.TestCase):
    """Test the SymptomInputs collection class"""

    def setUp(self):
        self.inputs = SymptomInputs()
        self.input1 = SymptomInput(1, "1", "I have a headache", "2024-01-01")
        self.input2 = SymptomInput(2, "2", "I have a fever", "2024-01-02")
        self.input3 = SymptomInput(3, "1", "I have a cough", "2024-01-03")

    def test_symptom_inputs_init(self):
        """Test symptom inputs collection initialization"""
        self.assertEqual(len(self.inputs.get_all_list()), 0)

    def test_symptom_inputs_add(self):
        """Test adding symptom inputs"""
        self.inputs.add(self.input1)
        self.assertEqual(len(self.inputs.get_all_list()), 1)

    def test_symptom_inputs_add_duplicate(self):
        """Test that duplicate inputs are not added"""
        self.inputs.add(self.input1)
        self.inputs.add(self.input1)
        self.assertEqual(len(self.inputs.get_all_list()), 1)

    def test_symptom_inputs_add_none(self):
        """Test that None is not added"""
        self.inputs.add(None)
        self.assertEqual(len(self.inputs.get_all_list()), 0)

    def test_symptom_inputs_filter_by_input_id(self):
        """Test filtering by input ID"""
        self.inputs.add(self.input1)
        self.inputs.add(self.input2)
        filtered = self.inputs.filter_by_input_id(1)
        self.assertEqual(len(filtered.get_all_list()), 1)

    def test_symptom_inputs_filter_by_user_id(self):
        """Test filtering by user ID"""
        self.inputs.add(self.input1)
        self.inputs.add(self.input2)
        self.inputs.add(self.input3)
        filtered = self.inputs.filter_by_user_id("1")
        self.assertEqual(len(filtered.get_all_list()), 2)

    def test_symptom_inputs_filter_by_created_at(self):
        """Test filtering by created_at"""
        self.inputs.add(self.input1)
        self.inputs.add(self.input2)
        filtered = self.inputs.filter_by_created_at("2024-01-01")
        self.assertEqual(len(filtered.get_all_list()), 1)


class TestSymptomInputsDatabase(unittest.TestCase):
    """Test symptom inputs database operations"""

    @patch('core.symptoms_input.coredb.getDBObject')
    def test_load_all_symptom_inputs(self, mock_get_db):
        """Test loading all symptom inputs from database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, "1", "I have a headache", "2024-01-01"),
            (2, "2", "I have a fever", "2024-01-02"),
            (3, "1", "I have a cough", "2024-01-03")
        ]

        inputs = load_all_symptom_inputs()
        self.assertEqual(len(inputs.get_all_list()), 3)
        mock_conn.close.assert_called_once()

    @patch('core.symptoms_input.coredb.getDBObject')
    def test_load_all_symptom_inputs_empty(self, mock_get_db):
        """Test loading inputs when database is empty"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        inputs = load_all_symptom_inputs()
        self.assertEqual(len(inputs.get_all_list()), 0)

    @patch('core.symptoms_input.coredb.getDBObject')
    def test_load_all_symptom_inputs_exception(self, mock_get_db):
        """Test loading inputs with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            inputs = load_all_symptom_inputs()
        self.assertEqual(len(inputs.get_all_list()), 0)

    @patch('core.symptoms_input.coredb.getDBObject')
    def test_add_new_symptom_input_success(self, mock_get_db):
        """Test adding a new symptom input"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        import core.symptoms_input
        core.symptoms_input.cache_all_symptom_inputs = None

        success = add_new_symptom_input("1", "I have a headache")
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('core.symptoms_input.coredb.getDBObject')
    def test_add_new_symptom_input_exception(self, mock_get_db):
        """Test adding a symptom input with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = add_new_symptom_input("1", "I have a headache")
        self.assertFalse(success)

    @patch('core.symptoms_input.coredb.getDBObject')
    def test_set_symptom_input_data_success(self, mock_get_db):
        """Test updating symptom input data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        import core.symptoms_input
        core.symptoms_input.cache_all_symptom_inputs = None

        success = set_symptom_input_data(1, "2", "Updated text", "2024-01-02")
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('core.symptoms_input.coredb.getDBObject')
    def test_set_symptom_input_data_exception(self, mock_get_db):
        """Test updating symptom input with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = set_symptom_input_data(1, "2", "Updated text", "2024-01-02")
        self.assertFalse(success)

    @patch('core.symptoms_input.load_all_symptom_inputs')
    def test_get_all_symptom_inputs_cache(self, mock_load):
        """Test getting symptom inputs cache"""
        mock_inputs = SymptomInputs()
        mock_inputs.add(SymptomInput(1, "1", "I have a headache", "2024-01-01"))
        mock_load.return_value = mock_inputs

        import core.symptoms_input
        core.symptoms_input.cache_all_symptom_inputs = None

        result = get_all_symptom_inputs_cache()
        self.assertEqual(len(result.get_all_list()), 1)


if __name__ == '__main__':
    unittest.main()
