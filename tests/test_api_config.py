#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.config import Settings, settings


class TestSettingsConfiguration(unittest.TestCase):
    """Test API configuration settings"""

    def test_settings_exists(self):
        """Test that settings object exists"""
        self.assertIsNotNone(settings)

    def test_settings_api_title(self):
        """Test API title setting"""
        self.assertEqual(settings.api_title, "Diagnoze AI API")

    def test_settings_api_version(self):
        """Test API version setting"""
        self.assertEqual(settings.api_version, "1.0.0")

    def test_settings_api_prefix(self):
        """Test API prefix setting"""
        self.assertEqual(settings.api_prefix, "/api/v1")

    def test_settings_security_defaults(self):
        """Test security settings"""
        self.assertIsNotNone(settings.secret_key)
        self.assertEqual(settings.algorithm, "HS256")
        self.assertEqual(settings.access_token_expire_minutes, 30)

    def test_settings_cors_origins(self):
        """Test CORS origins"""
        self.assertIsNotNone(settings.cors_origins)
        self.assertIsInstance(settings.cors_origins, list)
        self.assertGreater(len(settings.cors_origins), 0)

    def test_settings_database_url_optional(self):
        """Test that database URL is optional"""
        # Should not raise an error
        self.assertTrue(hasattr(settings, 'database_url'))


class TestSettingsClass(unittest.TestCase):
    """Test Settings class"""

    def test_settings_instantiation(self):
        """Test creating Settings instance"""
        test_settings = Settings()
        self.assertIsNotNone(test_settings)

    def test_settings_has_all_fields(self):
        """Test that settings has all required fields"""
        required_fields = [
            'api_title', 'api_version', 'api_prefix',
            'secret_key', 'algorithm', 'access_token_expire_minutes',
            'cors_origins'
        ]
        for field in required_fields:
            self.assertTrue(hasattr(settings, field))


if __name__ == '__main__':
    unittest.main()
