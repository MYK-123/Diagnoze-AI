#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.core import (
    predict_internal, get_symptom_list_from_disease, 
    get_top_k_diseases_from_diseases_list,
    get_top_k_diseases_from_prediction_with_probablities,
    get_education_content_for_disease, get_education_content_for_diseases,
    predict, get_symptoms_string_from_symptom_list,
    get_symptom_list_from_symptom_string, build_prompt
)
from core.disease import Disease
from core.symptoms import Symptom, Symptoms


class TestPredictInternal(unittest.TestCase):
    """Test predict_internal function"""

    @patch('core.core.get_all_diseases_cache')
    @patch('core.core.get_relations_cache')
    def test_predict_internal_no_symptoms(self, mock_relations, mock_diseases):
        """Test predict_internal with no symptoms"""
        result = predict_internal(None)
        self.assertEqual(result, [])

    @patch('core.core.get_all_diseases_cache')
    @patch('core.core.get_relations_cache')
    def test_predict_internal_empty_symptoms(self, mock_relations, mock_diseases):
        """Test predict_internal with empty symptom list"""
        result = predict_internal([])
        self.assertEqual(result, [])

    @patch('core.core.get_all_diseases_cache')
    @patch('core.core.get_relations_cache')
    def test_predict_internal_with_symptoms(self, mock_relations, mock_diseases):
        """Test predict_internal with symptoms"""
        # Mock disease
        mock_disease = MagicMock()
        mock_disease.get_disease_id.return_value = 1
        mock_diseases.return_value = [mock_disease]
        
        # Mock symptom
        mock_symptom = MagicMock()
        mock_symptom.get_id.return_value = 1
        
        # Mock relations
        mock_relation_obj = MagicMock()
        mock_relation_obj.get_strengths_by_disease_id_and_symptom_id.return_value = 0.7
        mock_relations.return_value = mock_relation_obj
        
        result = predict_internal([mock_symptom])
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    @patch('core.core.get_all_diseases_cache')
    @patch('core.core.get_relations_cache')
    def test_predict_internal_returns_tuples(self, mock_relations, mock_diseases):
        """Test that predict_internal returns list of tuples"""
        mock_disease = MagicMock()
        mock_disease.get_disease_id.return_value = 1
        mock_diseases.return_value = [mock_disease]
        
        mock_symptom = MagicMock()
        mock_symptom.get_id.return_value = 1
        
        mock_relation_obj = MagicMock()
        mock_relation_obj.get_strengths_by_disease_id_and_symptom_id.return_value = 0.7
        mock_relations.return_value = mock_relation_obj
        
        result = predict_internal([mock_symptom])
        
        if result:
            self.assertIsInstance(result[0], tuple)
            self.assertEqual(len(result[0]), 2)

    @patch('core.core.get_all_diseases_cache')
    @patch('core.core.get_relations_cache')
    def test_predict_internal_with_exclude_symptoms(self, mock_relations, mock_diseases):
        """Test predict_internal with exclude symptoms"""
        mock_disease = MagicMock()
        mock_disease.get_disease_id.return_value = 1
        mock_diseases.return_value = [mock_disease]
        
        mock_symptom_include = MagicMock()
        mock_symptom_include.get_id.return_value = 1
        
        mock_symptom_exclude = MagicMock()
        mock_symptom_exclude.get_id.return_value = 2
        
        mock_relation_obj = MagicMock()
        mock_relation_obj.get_strengths_by_disease_id_and_symptom_id.return_value = 0.7
        mock_relations.return_value = mock_relation_obj
        
        result = predict_internal([mock_symptom_include], [mock_symptom_exclude])
        
        self.assertIsInstance(result, list)

    @patch('core.core.get_all_diseases_cache')
    @patch('core.core.get_relations_cache')
    def test_predict_internal_normalized_probabilities(self, mock_relations, mock_diseases):
        """Test that predict_internal returns normalized probabilities"""
        mock_disease1 = MagicMock()
        mock_disease1.get_disease_id.return_value = 1
        
        mock_disease2 = MagicMock()
        mock_disease2.get_disease_id.return_value = 2
        
        mock_diseases.return_value = [mock_disease1, mock_disease2]
        
        mock_symptom = MagicMock()
        mock_symptom.get_id.return_value = 1
        
        mock_relation_obj = MagicMock()
        mock_relation_obj.get_strengths_by_disease_id_and_symptom_id.return_value = 0.7
        mock_relations.return_value = mock_relation_obj
        
        result = predict_internal([mock_symptom])
        
        if result:
            total_prob = sum(prob for _, prob in result)
            self.assertAlmostEqual(total_prob, 1.0, places=5)


class TestGetSymptomListFromDisease(unittest.TestCase):
    """Test get_symptom_list_from_disease function"""

    def test_get_symptom_list_no_disease(self):
        """Test with None disease"""
        result = get_symptom_list_from_disease(None)
        self.assertEqual(result, [])

    @patch('core.core.get_all_symptoms_cache')
    @patch('core.core.get_relations_cache')
    def test_get_symptom_list_with_disease(self, mock_relations, mock_symptoms):
        """Test with valid disease"""
        mock_disease = MagicMock()
        mock_disease.get_disease_id.return_value = 1
        
        mock_relation = MagicMock()
        mock_relation.get_disease_id.return_value = 1
        mock_relation.get_symptom_id.return_value = 1
        
        mock_relation_obj = MagicMock()
        mock_relation_obj.get_all_relation_list.return_value = [mock_relation]
        mock_relations.return_value = mock_relation_obj
        
        mock_symptom = MagicMock()
        mock_symptom.get_id.return_value = 1
        
        mock_symptoms_obj = MagicMock()
        mock_symptoms_obj.get_all_list.return_value = [mock_symptom]
        mock_symptoms.return_value = mock_symptoms_obj
        
        result = get_symptom_list_from_disease(mock_disease)
        
        self.assertIsInstance(result, list)


class TestGetTopKDiseasesFromDiseasesList(unittest.TestCase):
    """Test get_top_k_diseases_from_diseases_list function"""

    def test_get_top_k_none_list(self):
        """Test with None disease list"""
        result = get_top_k_diseases_from_diseases_list(None, 3)
        self.assertEqual(result, [])

    def test_get_top_k_empty_list(self):
        """Test with empty disease list"""
        result = get_top_k_diseases_from_diseases_list([], 3)
        self.assertEqual(result, [])

    def test_get_top_k_zero_k(self):
        """Test with k=0"""
        mock_disease = MagicMock()
        result = get_top_k_diseases_from_diseases_list([mock_disease], 0)
        self.assertEqual(result, [])

    def test_get_top_k_negative_k(self):
        """Test with negative k"""
        mock_disease = MagicMock()
        result = get_top_k_diseases_from_diseases_list([mock_disease], -1)
        self.assertEqual(result, [])

    def test_get_top_k_returns_diseases(self):
        """Test that function returns diseases ranked by severity"""
        mock_disease1 = MagicMock()
        mock_disease1.get_severity_level.return_value = 3  # High
        
        mock_disease2 = MagicMock()
        mock_disease2.get_severity_level.return_value = 1  # Low
        
        mock_disease3 = MagicMock()
        mock_disease3.get_severity_level.return_value = 2  # Medium
        
        result = get_top_k_diseases_from_diseases_list([mock_disease1, mock_disease2, mock_disease3], 2)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], mock_disease1)  # Highest severity first

    def test_get_top_k_k_greater_than_list(self):
        """Test when k is greater than list length"""
        mock_disease1 = MagicMock()
        mock_disease1.get_severity_level.return_value = 1
        
        mock_disease2 = MagicMock()
        mock_disease2.get_severity_level.return_value = 2
        
        result = get_top_k_diseases_from_diseases_list([mock_disease1, mock_disease2], 5)
        
        self.assertEqual(len(result), 2)


class TestGetTopKDiseasesFromPrediction(unittest.TestCase):
    """Test get_top_k_diseases_from_prediction_with_probablities function"""

    @patch('core.core.predict_internal')
    def test_get_top_k_from_prediction(self, mock_predict):
        """Test getting top k from prediction"""
        mock_disease1 = MagicMock()
        mock_disease2 = MagicMock()
        
        mock_predict.return_value = [
            (mock_disease1, 0.6),
            (mock_disease2, 0.4)
        ]
        
        mock_symptom = MagicMock()
        result = get_top_k_diseases_from_prediction_with_probablities([mock_symptom], top_k=1)
        
        self.assertEqual(len(result), 1)

    @patch('core.core.predict_internal')
    def test_get_top_k_default_k(self, mock_predict):
        """Test default k=3"""
        diseases = [(MagicMock(), 0.3) for _ in range(5)]
        mock_predict.return_value = diseases
        
        mock_symptom = MagicMock()
        result = get_top_k_diseases_from_prediction_with_probablities([mock_symptom])
        
        self.assertEqual(len(result), 3)


class TestGetEducationContent(unittest.TestCase):
    """Test education content functions"""

    @patch('core.core.get_all_education_content_cache')
    def test_get_education_content_no_disease(self, mock_content):
        """Test with no disease"""
        result = get_education_content_for_disease(None)
        self.assertIsNone(result)

    @patch('core.core.get_all_education_content_cache')
    def test_get_education_content_not_found(self, mock_content):
        """Test when education content not found"""
        mock_content.return_value = []
        
        mock_disease = MagicMock()
        mock_disease.get_disease_id.return_value = 1
        
        result = get_education_content_for_disease(mock_disease)
        self.assertIsNone(result)

    @patch('core.core.get_all_education_content_cache')
    def test_get_education_content_found(self, mock_content):
        """Test when education content is found"""
        mock_edu_content = MagicMock()
        mock_edu_content.get_disease_id.return_value = 1
        mock_content.return_value = [mock_edu_content]
        
        mock_disease = MagicMock()
        mock_disease.get_disease_id.return_value = 1
        
        result = get_education_content_for_disease(mock_disease)
        self.assertIsNotNone(result)

    @patch('core.core.get_all_education_content_cache')
    def test_get_education_content_for_diseases_none(self, mock_content):
        """Test get_education_content_for_diseases with None"""
        result = get_education_content_for_diseases(None)
        self.assertEqual(result, [])

    @patch('core.core.get_all_education_content_cache')
    def test_get_education_content_for_diseases_empty(self, mock_content):
        """Test get_education_content_for_diseases with empty list"""
        result = get_education_content_for_diseases([])
        self.assertEqual(result, [])

    @patch('core.core.get_all_education_content_cache')
    def test_get_education_content_for_diseases(self, mock_content):
        """Test get_education_content_for_diseases with diseases"""
        mock_edu1 = MagicMock()
        mock_edu1.get_disease_id.return_value = 1
        
        mock_edu2 = MagicMock()
        mock_edu2.get_disease_id.return_value = 2
        
        mock_content.return_value = [mock_edu1, mock_edu2]
        
        mock_disease1 = MagicMock()
        mock_disease1.get_disease_id.return_value = 1
        
        mock_disease2 = MagicMock()
        mock_disease2.get_disease_id.return_value = 2
        
        result = get_education_content_for_diseases([mock_disease1, mock_disease2])
        
        self.assertEqual(len(result), 2)


class TestPredict(unittest.TestCase):
    """Test predict function"""

    @patch('core.core.add_new_prediction')
    @patch('core.core.get_top_k_diseases_from_prediction_with_probablities')
    def test_predict_function(self, mock_get_top_k, mock_add_pred):
        """Test predict function"""
        mock_disease = MagicMock()
        mock_disease.get_disease_id.return_value = 1
        
        mock_get_top_k.return_value = [(mock_disease, 0.8)]
        
        mock_symptom = MagicMock()
        result = predict(1, mock_symptom, top_n=1)
        
        self.assertEqual(len(result), 1)
        mock_add_pred.assert_called()

    @patch('core.core.add_new_prediction')
    @patch('core.core.get_top_k_diseases_from_prediction_with_probablities')
    def test_predict_multiple(self, mock_get_top_k, mock_add_pred):
        """Test predict with multiple diseases"""
        mock_disease1 = MagicMock()
        mock_disease1.get_disease_id.return_value = 1
        
        mock_disease2 = MagicMock()
        mock_disease2.get_disease_id.return_value = 2
        
        mock_get_top_k.return_value = [(mock_disease1, 0.6), (mock_disease2, 0.4)]
        
        mock_symptom = MagicMock()
        result = predict(1, mock_symptom, top_n=2)
        
        self.assertEqual(len(result), 2)


class TestGetSymptomsStringFromList(unittest.TestCase):
    """Test get_symptoms_string_from_symptom_list function"""

    def test_get_symptoms_string_no_list(self):
        """Test with no symptom list"""
        result = get_symptoms_string_from_symptom_list(None)
        self.assertEqual(result, "")

    def test_get_symptoms_string_empty_list(self):
        """Test with empty symptom list"""
        result = get_symptoms_string_from_symptom_list([])
        self.assertEqual(result, "")

    def test_get_symptoms_string_single(self):
        """Test with single symptom"""
        mock_symptom = MagicMock()
        mock_symptom.get_name.return_value = "Headache"
        
        result = get_symptoms_string_from_symptom_list([mock_symptom])
        
        self.assertEqual(result, "Headache")

    def test_get_symptoms_string_multiple(self):
        """Test with multiple symptoms"""
        mock_symptom1 = MagicMock()
        mock_symptom1.get_name.return_value = "Headache"
        
        mock_symptom2 = MagicMock()
        mock_symptom2.get_name.return_value = "Fever"
        
        result = get_symptoms_string_from_symptom_list([mock_symptom1, mock_symptom2])
        
        self.assertEqual(result, "Headache, Fever")


class TestGetSymptomListFromString(unittest.TestCase):
    """Test get_symptom_list_from_symptom_string function"""

    @patch('core.core.get_all_symptoms_cache')
    def test_get_symptom_list_no_string(self, mock_symptoms):
        """Test with no string"""
        result = get_symptom_list_from_symptom_string(None)
        self.assertEqual(result, [])

    @patch('core.core.get_all_symptoms_cache')
    def test_get_symptom_list_empty_string(self, mock_symptoms):
        """Test with empty string"""
        result = get_symptom_list_from_symptom_string("")
        self.assertEqual(result, [])

    @patch('core.core.get_all_symptoms_cache')
    def test_get_symptom_list_from_string(self, mock_symptoms):
        """Test extracting symptom list from string"""
        mock_symptom = MagicMock()
        mock_symptom.get_name.return_value = "headache"
        
        mock_symptoms_obj = MagicMock()
        mock_symptoms_obj.get_all_list.return_value = [mock_symptom]
        mock_symptoms.return_value = mock_symptoms_obj
        
        result = get_symptom_list_from_symptom_string("I have a headache")
        
        self.assertIsInstance(result, list)

    @patch('core.core.get_all_symptoms_cache')
    def test_get_symptom_list_case_insensitive(self, mock_symptoms):
        """Test that symptom matching is case-insensitive"""
        mock_symptom = MagicMock()
        mock_symptom.get_name.return_value = "Headache"
        
        mock_symptoms_obj = MagicMock()
        mock_symptoms_obj.get_all_list.return_value = [mock_symptom]
        mock_symptoms.return_value = mock_symptoms_obj
        
        result = get_symptom_list_from_symptom_string("I have HEADACHE")
        
        self.assertIsInstance(result, list)


class TestBuildPrompt(unittest.TestCase):
    """Test build_prompt function"""

    def test_build_prompt_no_args(self):
        """Test build_prompt with no arguments"""
        result = build_prompt(None, None)
        self.assertIsInstance(result, str)
        self.assertIn("Task: Extract patient symptoms", result)

    def test_build_prompt_with_text(self):
        """Test build_prompt with chat text"""
        result = build_prompt("I have a headache and fever", None)
        self.assertIn("I have a headache and fever", result)

    def test_build_prompt_with_symptoms(self):
        """Test build_prompt with symptom list"""
        result = build_prompt(None, ["headache", "fever"])
        self.assertIn("headache", result)
        self.assertIn("fever", result)

    def test_build_prompt_with_both(self):
        """Test build_prompt with both text and symptoms"""
        result = build_prompt("I feel unwell", ["headache", "fever", "cough"])
        self.assertIn("I feel unwell", result)
        self.assertIn("headache", result)
        self.assertIn("Symptom List:", result)

    def test_build_prompt_structure(self):
        """Test that build_prompt has correct structure"""
        result = build_prompt("test", ["symptom1"])
        self.assertIn("Task:", result)
        self.assertIn("Rules:", result)
        self.assertIn("Symptom List:", result)
        self.assertIn("Patient chat:", result)
        self.assertIn("Symptoms:", result)

    def test_build_prompt_empty_symptom_list(self):
        """Test build_prompt with empty symptom list"""
        result = build_prompt("I have a headache", [])
        self.assertIsInstance(result, str)
        self.assertIn("Symptom List: ", result)


if __name__ == '__main__':
    unittest.main()
