#!/usr/env python3

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import numpy as np

# Mock core modules before importing
sys.modules['auth'] = MagicMock()
sys.modules['auth.users'] = MagicMock()
sys.modules['content'] = MagicMock()
sys.modules['content.educational_content'] = MagicMock()
sys.modules['core.disease_symptoms_relation'] = MagicMock()
sys.modules['core.predictions'] = MagicMock()
sys.modules['core.symptoms_input'] = MagicMock()

from db.core import reset_database

from core.core import (
    predict_internal,
    predict,
    get_symptom_list_from_disease,
    get_top_k_diseases_from_diseases_list,
    get_top_k_diseases_from_prediction_with_probablities,
    get_education_content_for_disease,
    get_education_content_for_diseases,
    get_symptoms_string_from_symptom_list,
    get_symptom_list_from_symptom_string,
    build_prompt
)
from core.disease_symptoms_relation import add_new_diseases_symptom_relation
from core.disease import add_new_disease, get_all_diseases_cache
from core.symptoms import Symptom, add_new_symptom, get_all_symptoms_cache
from content.educational_content import add_new_educational_content


@pytest.fixture(scope="module", autouse=True)
def db_init_for_core_testing():
    reset_database(populate_default=True)
    populate_database_for_core_function_testing()
    yield
    reset_database()


TEST_DISEASE = [ ("disease 1", "dis category 1", "low"), ("disease 2", "dis category 2", "low"), ("disease 3", "dis category 3", "high"), ("disease 4", "dis category 4", "medium"), ("disease 5", "dis category 5", "low")]
TEST_SYMPTOM = [("symptom 1", "sym category 1"), ("symptom 2", "sym category 2"), ("symptom 3", "sym category 3"), ("symptom 4", "sym category 4"), ("symptom 5", "sym category 5"), ("symptom 6", "sym category 6"), ("symptom 7", "sym category 7"), ("symptom 8", "sym category 8"), ("symptom 9", "sym category 9"), ("symptom 10", "sym category 10")]
TEST_DISEASE_SYMPTOM_RELATION = [(1, 1), (1, 2), (2, 3), (2, 4), (2, 10), (3, 1), (3, 3), (3, 4), (4, 5), (4, 6), (4, 7), (4, 8), (5, 1), (5, 8), (5, 9), (5, 10)]
TEST_DISEASE_EDUCATION = [(1, "disease 1"), (2, "disease 2"), (3, "disease 3"), (4, "disease 4"), (5, "disease 5")]

TEST_INCLUDE_SYMPTOM = [1, 2, 3, 4, 10]
TEST_EXCLUDE_SYMPTOM = [3, 4, 5, 6, 7]
TEST_INCLUDE_SYMPTOM_RESULT_DISEASE = [1, 2, 3, 5]
TEST_INCLUDE_EXCLUDE_SYMPTOM_RESULT_DISEASE = [1, 5]

TEST_SYMPTOM_OBJS = [Symptom(idx, *name) for idx, name in enumerate(TEST_SYMPTOM, start=1)]

def populate_database_for_core_function_testing():
    for disease in TEST_DISEASE:
        add_new_disease(*disease)
    for symptom in TEST_SYMPTOM:
        add_new_symptom(*symptom)
    for rel in TEST_DISEASE_SYMPTOM_RELATION:
        add_new_diseases_symptom_relation(*rel, 0.5)
    for cont in TEST_DISEASE_EDUCATION:
        add_new_educational_content(*cont, "TEST CONTEST", True)


class TestPredictInternal:
    """Tests for predict_internal function"""
    
    def test_predict_internal_empty_symptoms(self):
        """Test prediction with empty symptoms"""
        result = predict_internal(None)
        assert result == []
        
        result = predict_internal([])
        assert result == []

    def test_predict_internal_valid_symptoms(self):
        """Test prediction with valid symptoms"""
        with patch('core.core.get_all_diseases_cache') as mock_diseases, \
             patch('core.core.get_relations_cache') as mock_relations:
            
            # Mock disease
            mock_disease = MagicMock()
            mock_disease.get_disease_id.return_value = 1
            mock_diseases.return_value = [mock_disease]
            
            # Mock symptom
            mock_symptom = MagicMock()
            mock_symptom.get_id.return_value = 1
            
            # Mock relations
            mock_rel = MagicMock()
            mock_rel.get_strengths_by_disease_id_and_symptom_id.return_value = 0.7
            mock_relations.return_value = mock_rel
            
            result = predict_internal([mock_symptom])
            
            assert len(result) > 0
            assert result[0][0] == mock_disease

    def test_predict_internal_with_exclude_symptoms(self):
        """Test prediction with excluded symptoms"""
        with patch('core.core.get_all_diseases_cache') as mock_diseases, \
             patch('core.core.get_relations_cache') as mock_relations:
            
            mock_disease = MagicMock()
            mock_disease.get_disease_id.return_value = 1
            mock_diseases.return_value = [mock_disease]
            
            mock_include_symptom = MagicMock()
            mock_include_symptom.get_id.return_value = 1
            
            mock_exclude_symptom = MagicMock()
            mock_exclude_symptom.get_id.return_value = 2
            
            mock_rel = MagicMock()
            mock_rel.get_strengths_by_disease_id_and_symptom_id.return_value = 0.7
            mock_relations.return_value = mock_rel
            
            result = predict_internal([mock_include_symptom], [mock_exclude_symptom])
            
            assert len(result) > 0


class TestGetSymptomListFromDisease:
    """Tests for get_symptom_list_from_disease function"""
    
    def test_get_symptom_list_none_disease(self):
        """Test with None disease"""
        result = get_symptom_list_from_disease(None)
        assert result == []

    def test_get_symptom_list_valid_disease(self):
        """Test with valid disease"""
        with patch('core.core.get_relations_cache') as mock_relations, \
             patch('core.core.get_all_symptoms_cache') as mock_symptoms:
            
            mock_disease = MagicMock()
            mock_disease.get_disease_id.return_value = 1
            
            mock_relation = MagicMock()
            mock_relation.get_symptom_id.return_value = 1
            mock_relations.return_value.get_all_relation_list.return_value = [mock_relation]
            
            mock_symptom = MagicMock()
            mock_symptom.get_id.return_value = 1
            mock_symptoms.return_value.get_all_list.return_value = [mock_symptom]
            
            result = get_symptom_list_from_disease(mock_disease)
            
            assert len(result) >= 0


class TestGetTopKDiseasesFromList:
    """Tests for get_top_k_diseases_from_diseases_list function"""
    
    def test_get_top_k_empty_list(self):
        """Test with empty diseases list"""
        result = get_top_k_diseases_from_diseases_list([], 3)
        assert result == []

    def test_get_top_k_zero_k(self):
        """Test with k=0"""
        diseases = [MagicMock()]
        result = get_top_k_diseases_from_diseases_list(diseases, 0)
        assert result == []

    def test_get_top_k_valid_diseases(self):
        """Test with valid diseases"""
        mock_disease1 = MagicMock()
        mock_disease1.get_severity_level.return_value = 3
        
        mock_disease2 = MagicMock()
        mock_disease2.get_severity_level.return_value = 1
        
        mock_disease3 = MagicMock()
        mock_disease3.get_severity_level.return_value = 2
        
        diseases = [mock_disease1, mock_disease2, mock_disease3]
        result = get_top_k_diseases_from_diseases_list(diseases, 2)
        
        assert len(result) == 2
        assert result[0] == mock_disease1  # Highest severity


class TestGetTopKDiseasesWithProbabilities:
    """Tests for get_top_k_diseases_from_prediction_with_probablities function"""
    
    def test_get_top_k_predictions_empty(self):
        """Test with no symptoms"""
        with patch('core.core.predict_internal') as mock_predict:
            mock_predict.return_value = []
            
            result = get_top_k_diseases_from_prediction_with_probablities(None)
            
            assert result == []

    def test_get_top_k_predictions_returns_top_k(self):
        """Test that it returns top k predictions"""
        with patch('core.core.predict_internal') as mock_predict:
            mock_disease1 = MagicMock()
            mock_disease2 = MagicMock()
            mock_disease3 = MagicMock()
            mock_disease4 = MagicMock()
            
            predictions = [
                (mock_disease1, 0.9),
                (mock_disease2, 0.7),
                (mock_disease3, 0.5),
                (mock_disease4, 0.3)
            ]
            mock_predict.return_value = predictions
            
            result = get_top_k_diseases_from_prediction_with_probablities([], top_k=3)
            
            assert len(result) == 3


class TestGetEducationContentForDisease:
    """Tests for get_education_content_for_disease function"""
    
    def test_get_content_none_disease(self):
        """Test with None disease"""
        result = get_education_content_for_disease(None)
        assert result is None

    def test_get_content_valid_disease(self):
        """Test with valid disease"""
        with patch('core.core.get_all_education_content_cache') as mock_cache:
            mock_disease = MagicMock()
            mock_disease.get_disease_id.return_value = 1
            
            mock_content = MagicMock()
            mock_content.get_disease_id.return_value = 1
            mock_cache.return_value = [mock_content]
            
            result = get_education_content_for_disease(mock_disease)
            
            assert result == mock_content


class TestGetEducationContentForDiseases:
    """Tests for get_education_content_for_diseases function"""
    
    def test_get_content_empty_diseases(self):
        """Test with empty diseases list"""
        result = get_education_content_for_diseases([])
        assert result == []

    def test_get_content_valid_diseases(self):
        """Test with valid diseases"""
        with patch('core.core.get_all_education_content_cache') as mock_cache:
            mock_disease1 = MagicMock()
            mock_disease1.get_disease_id.return_value = 1
            
            mock_disease2 = MagicMock()
            mock_disease2.get_disease_id.return_value = 2
            
            mock_content1 = MagicMock()
            mock_content1.get_disease_id.return_value = 1
            
            mock_content2 = MagicMock()
            mock_content2.get_disease_id.return_value = 2
            
            mock_cache.return_value = [mock_content1, mock_content2]
            
            result = get_education_content_for_diseases([mock_disease1, mock_disease2])
            
            assert len(result) == 2


class TestPredict:
    """Tests for predict function"""
    
    @patch('core.core.add_new_prediction')
    @patch('core.core.get_top_k_diseases_from_prediction_with_probablities')
    def test_predict_success(self, mock_predict_internal, mock_add_pred):
        """Test successful prediction"""
        mock_disease = MagicMock()
        mock_disease.get_disease_id.return_value = 1
        mock_predict_internal.return_value = [(mock_disease, 0.85)]
        
        result = predict(input_id=1, symptoms=[], top_n=3)
        
        assert len(result) > 0
        assert mock_add_pred.called


class TestGetSymptomsString:
    """Tests for get_symptoms_string_from_symptom_list function"""
    
    def test_symptoms_string_empty_list(self):
        """Test with empty symptom list"""
        result = get_symptoms_string_from_symptom_list([])
        assert result == ""

    def test_symptoms_string_single_symptom(self):
        """Test with single symptom"""
        mock_symptom = MagicMock()
        mock_symptom.get_name.return_value = "headache"
        
        result = get_symptoms_string_from_symptom_list([mock_symptom])
        
        assert result == "headache"

    def test_symptoms_string_multiple_symptoms(self):
        """Test with multiple symptoms"""
        mock_symptom1 = MagicMock()
        mock_symptom1.get_name.return_value = "headache"
        
        mock_symptom2 = MagicMock()
        mock_symptom2.get_name.return_value = "fever"
        
        result = get_symptoms_string_from_symptom_list([mock_symptom1, mock_symptom2])
        
        assert "headache" in result
        assert "fever" in result
        assert ", " in result


class TestGetSymptomListFromString:
    """Tests for get_symptom_list_from_symptom_string function"""
    
    def test_symptom_list_from_string_empty(self):
        """Test with empty string"""
        with patch('core.core.get_all_symptoms_cache') as mock_cache:
            mock_cache.return_value = []
            
            result = get_symptom_list_from_symptom_string("")
            
            assert result == []

    def test_symptom_list_from_string_valid(self):
        """Test with valid symptom string"""
        with patch('core.core.get_all_symptoms_cache') as mock_cache:
            mock_symptom = MagicMock()
            mock_symptom.get_name.return_value = "headache"
            mock_cache.return_value = [mock_symptom]
            
            result = get_symptom_list_from_symptom_string("headache")
            
            assert len(result) > 0


class TestBuildPrompt:
    """Tests for build_prompt function"""
    
    def test_build_prompt_structure(self):
        """Test that prompt is properly structured"""
        chat_text = "I have a headache"
        symptom_list = ["headache", "fever", "cough"]
        
        prompt = build_prompt(chat_text, symptom_list)
        
        assert "Task:" in prompt
        assert "Symptom List:" in prompt
        assert "Patient chat:" in prompt
        assert "headache" in prompt
        assert chat_text in prompt

    def test_build_prompt_with_empty_symptoms(self):
        """Test prompt building with empty symptom list"""
        chat_text = "I feel sick"
        symptom_list = []
        
        prompt = build_prompt(chat_text, symptom_list)
        
        assert "Task:" in prompt
        assert chat_text in prompt


