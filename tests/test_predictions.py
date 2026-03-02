#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.predictions import (
    Prediction, Predictions,
    load_all_predictions, add_new_prediction,
    set_prediction_data, get_all_predictions_cache
)


class TestPrediction(unittest.TestCase):
    """Test the Prediction entity class"""

    def setUp(self):
        self.prediction = Prediction(1, 1, 2, 0.92)

    def test_prediction_init(self):
        """Test prediction initialization"""
        self.assertEqual(self.prediction.get_prediction_id(), 1)
        self.assertEqual(self.prediction.get_input_id(), 1)
        self.assertEqual(self.prediction.get_disease_id(), 2)
        self.assertEqual(self.prediction.get_confidence_score(), 0.92)

    def test_prediction_getters(self):
        """Test all prediction getters"""
        self.assertEqual(self.prediction.get_prediction_id(), 1)
        self.assertEqual(self.prediction.get_input_id(), 1)
        self.assertEqual(self.prediction.get_disease_id(), 2)
        self.assertEqual(self.prediction.get_confidence_score(), 0.92)

    def test_prediction_update(self):
        """Test prediction update"""
        self.prediction.update(2, 3, 0.75)
        self.assertEqual(self.prediction.get_input_id(), 2)
        self.assertEqual(self.prediction.get_disease_id(), 3)
        self.assertEqual(self.prediction.get_confidence_score(), 0.75)

    def test_prediction_equality(self):
        """Test prediction equality by ID"""
        pred2 = Prediction(1, 5, 6, 0.5)
        pred3 = Prediction(2, 1, 2, 0.92)
        self.assertEqual(self.prediction, pred2)
        self.assertNotEqual(self.prediction, pred3)

    def test_prediction_hash(self):
        """Test prediction hashing"""
        pred2 = Prediction(1, 5, 6, 0.5)
        self.assertEqual(hash(self.prediction), hash(pred2))

    def test_prediction_equality_non_prediction(self):
        """Test equality with non-Prediction objects"""
        self.assertNotEqual(self.prediction, "Not a prediction")
        self.assertNotEqual(self.prediction, 1)


class TestPredictions(unittest.TestCase):
    """Test the Predictions collection class"""

    def setUp(self):
        self.predictions = Predictions()
        self.pred1 = Prediction(1, 1, 2, 0.92)
        self.pred2 = Prediction(2, 1, 3, 0.65)
        self.pred3 = Prediction(3, 2, 2, 0.85)

    def test_predictions_init(self):
        """Test predictions collection initialization"""
        self.assertEqual(len(self.predictions.get_all_list()), 0)

    def test_predictions_add(self):
        """Test adding predictions"""
        self.predictions.add(self.pred1)
        self.assertEqual(len(self.predictions.get_all_list()), 1)

    def test_predictions_add_duplicate(self):
        """Test that duplicate predictions are not added"""
        self.predictions.add(self.pred1)
        self.predictions.add(self.pred1)
        self.assertEqual(len(self.predictions.get_all_list()), 1)

    def test_predictions_add_none(self):
        """Test that None is not added"""
        self.predictions.add(None)
        self.assertEqual(len(self.predictions.get_all_list()), 0)

    def test_predictions_filter_by_prediction_id(self):
        """Test filtering by prediction ID"""
        self.predictions.add(self.pred1)
        self.predictions.add(self.pred2)
        filtered = self.predictions.filter_by_prediction_id(1)
        self.assertEqual(len(filtered.get_all_list()), 1)

    def test_predictions_filter_by_input_id(self):
        """Test filtering by input ID"""
        self.predictions.add(self.pred1)
        self.predictions.add(self.pred2)
        self.predictions.add(self.pred3)
        filtered = self.predictions.filter_by_input_id(1)
        self.assertEqual(len(filtered.get_all_list()), 2)

    def test_predictions_filter_by_disease_id(self):
        """Test filtering by disease ID"""
        self.predictions.add(self.pred1)
        self.predictions.add(self.pred2)
        self.predictions.add(self.pred3)
        filtered = self.predictions.filter_by_disease_id(2)
        self.assertEqual(len(filtered.get_all_list()), 2)

    def test_predictions_filter_by_confidence_score(self):
        """Test filtering by exact confidence score"""
        self.predictions.add(self.pred1)
        self.predictions.add(self.pred2)
        filtered = self.predictions.filter_by_confidence_score(0.92)
        self.assertEqual(len(filtered.get_all_list()), 1)

    def test_predictions_filter_by_confidence_min(self):
        """Test filtering by minimum confidence score"""
        self.predictions.add(self.pred1)
        self.predictions.add(self.pred2)
        self.predictions.add(self.pred3)
        filtered = self.predictions.filter_by_confidence_min(0.8)
        self.assertEqual(len(filtered.get_all_list()), 2)

    def test_predictions_filter_by_confidence_max(self):
        """Test filtering by maximum confidence score"""
        self.predictions.add(self.pred1)
        self.predictions.add(self.pred2)
        self.predictions.add(self.pred3)
        filtered = self.predictions.filter_by_confidence_max(0.8)
        self.assertEqual(len(filtered.get_all_list()), 1)

    def test_predictions_filter_by_confidence_range(self):
        """Test filtering by confidence range"""
        self.predictions.add(self.pred1)
        self.predictions.add(self.pred2)
        self.predictions.add(self.pred3)
        filtered = self.predictions.filter_by_confidence_range(0.7, 0.9)
        self.assertEqual(len(filtered.get_all_list()), 1)


class TestPredictionsDatabase(unittest.TestCase):
    """Test predictions database operations"""

    @patch('core.predictions.coredb.getDBObject')
    def test_load_all_predictions(self, mock_get_db):
        """Test loading all predictions from database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (1, 1, 2, 0.92),
            (2, 1, 3, 0.65),
            (3, 2, 2, 0.85)
        ]

        predictions = load_all_predictions()
        self.assertEqual(len(predictions.get_all_list()), 3)
        mock_conn.close.assert_called_once()

    @patch('core.predictions.coredb.getDBObject')
    def test_load_all_predictions_empty(self, mock_get_db):
        """Test loading predictions when database is empty"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        predictions = load_all_predictions()
        self.assertEqual(len(predictions.get_all_list()), 0)

    @patch('core.predictions.coredb.getDBObject')
    def test_load_all_predictions_exception(self, mock_get_db):
        """Test loading predictions with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            predictions = load_all_predictions()
        self.assertEqual(len(predictions.get_all_list()), 0)

    @patch('core.predictions.coredb.getDBObject')
    def test_add_new_prediction_success(self, mock_get_db):
        """Test adding a new prediction"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        import core.predictions
        core.predictions.cache_all_predictions = None

        success = add_new_prediction(1, 2, 0.92)
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('core.predictions.coredb.getDBObject')
    def test_add_new_prediction_exception(self, mock_get_db):
        """Test adding a prediction with database exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = add_new_prediction(1, 2, 0.92)
        self.assertFalse(success)

    @patch('core.predictions.coredb.getDBObject')
    def test_set_prediction_data_success(self, mock_get_db):
        """Test updating prediction data"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        import core.predictions
        core.predictions.cache_all_predictions = None

        success = set_prediction_data(1, 2, 3, 0.75)
        self.assertTrue(success)
        mock_conn.commit.assert_called_once()

    @patch('core.predictions.coredb.getDBObject')
    def test_set_prediction_data_exception(self, mock_get_db):
        """Test updating prediction with exception"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with patch('builtins.print'):
            success = set_prediction_data(1, 2, 3, 0.75)
        self.assertFalse(success)

    @patch('core.predictions.load_all_predictions')
    def test_get_all_predictions_cache(self, mock_load):
        """Test getting predictions cache"""
        mock_predictions = Predictions()
        mock_predictions.add(Prediction(1, 1, 2, 0.92))
        mock_load.return_value = mock_predictions

        import core.predictions
        core.predictions.cache_all_predictions = None

        result = get_all_predictions_cache()
        self.assertEqual(len(result.get_all_list()), 1)


if __name__ == '__main__':
    unittest.main()
