#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.train import build_training_prompt, get_training_data


class TestBuildTrainingPrompt(unittest.TestCase):
    """Test training prompt building"""

    def test_build_training_prompt_basic(self):
        """Test basic prompt building"""
        symptoms = ["headache", "fever", "cough"]
        chat_text = "I have a headache and fever"
        
        prompt = build_training_prompt(symptoms, chat_text)
        
        self.assertIn("Task: Extract patient symptoms", prompt)
        self.assertIn("headache", prompt)
        self.assertIn("fever", prompt)
        self.assertIn("cough", prompt)
        self.assertIn(chat_text, prompt)

    def test_build_training_prompt_empty_symptoms(self):
        """Test prompt building with empty symptoms"""
        symptoms = []
        chat_text = "I have a headache"
        
        prompt = build_training_prompt(symptoms, chat_text)
        
        self.assertIn("Task: Extract patient symptoms", prompt)
        self.assertIn(chat_text, prompt)

    def test_build_training_prompt_empty_chat(self):
        """Test prompt building with empty chat"""
        symptoms = ["headache", "fever"]
        chat_text = ""
        
        prompt = build_training_prompt(symptoms, chat_text)
        
        self.assertIn("Task: Extract patient symptoms", prompt)
        self.assertIn("headache", prompt)

    def test_build_training_prompt_single_symptom(self):
        """Test prompt building with single symptom"""
        symptoms = ["headache"]
        chat_text = "My head hurts"
        
        prompt = build_training_prompt(symptoms, chat_text)
        
        self.assertIn("headache", prompt)
        self.assertIn("My head hurts", prompt)

    def test_build_training_prompt_structure(self):
        """Test that prompt has correct structure"""
        symptoms = ["headache"]
        chat_text = "test"
        
        prompt = build_training_prompt(symptoms, chat_text)
        
        self.assertIn("Rules:", prompt)
        self.assertIn("Symptom List:", prompt)
        self.assertIn("Patient chat:", prompt)
        self.assertIn("Symptoms:", prompt)

    def test_build_training_prompt_special_characters(self):
        """Test prompt building with special characters"""
        symptoms = ["pain (sharp)", "fever-high"]
        chat_text = "I have sharp pain & high fever"
        
        prompt = build_training_prompt(symptoms, chat_text)
        
        self.assertIn("pain (sharp)", prompt)
        self.assertIn("fever-high", prompt)


class TestGetTrainingData(unittest.TestCase):
    """Test training data retrieval"""

    def test_get_training_data_basic(self):
        """Test basic training data creation"""
        input_data = "Patient chat: I have a headache"
        output_data = "headache"
        
        result = get_training_data(input_data, output_data)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["input"], input_data)
        self.assertEqual(result["target"], output_data)

    def test_get_training_data_empty_input(self):
        """Test training data with empty input"""
        input_data = ""
        output_data = "symptom"
        
        result = get_training_data(input_data, output_data)
        
        self.assertEqual(result["input"], "")
        self.assertEqual(result["target"], "symptom")

    def test_get_training_data_empty_output(self):
        """Test training data with empty output"""
        input_data = "some input"
        output_data = ""
        
        result = get_training_data(input_data, output_data)
        
        self.assertEqual(result["input"], "some input")
        self.assertEqual(result["target"], "")

    def test_get_training_data_long_strings(self):
        """Test training data with long strings"""
        input_data = "This is a very long patient chat describing multiple symptoms in detail" * 10
        output_data = "symptom1, symptom2, symptom3"
        
        result = get_training_data(input_data, output_data)
        
        self.assertIn("very long", result["input"])
        self.assertIn("symptom1", result["target"])

    def test_get_training_data_special_characters(self):
        """Test training data with special characters"""
        input_data = "Patient says: 'I have pain & fever @ home'"
        output_data = "pain, fever"
        
        result = get_training_data(input_data, output_data)
        
        self.assertEqual(result["input"], input_data)
        self.assertEqual(result["target"], output_data)

    def test_get_training_data_return_structure(self):
        """Test that return structure has correct keys"""
        result = get_training_data("input", "output")
        
        self.assertIn("input", result)
        self.assertIn("target", result)
        self.assertEqual(len(result), 2)

    def test_get_training_data_unicode(self):
        """Test training data with unicode characters"""
        input_data = "Patient has café syndrome"
        output_data = "symptom"
        
        result = get_training_data(input_data, output_data)
        
        self.assertIn("café", result["input"])


if __name__ == '__main__':
    unittest.main()
