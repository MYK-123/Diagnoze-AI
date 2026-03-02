#!/usr/bin/env python3

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from safety.disclaimer import *


class TestDisclaimerModule(unittest.TestCase):
    """Test safety.disclaimer module"""

    def test_module_import(self):
        """Test that disclaimer module can be imported"""
        import safety.disclaimer
        self.assertIsNotNone(safety.disclaimer)

    def test_module_exists(self):
        """Test that disclaimer module exists"""
        try:
            import safety.disclaimer
            exists = True
        except ImportError:
            exists = False
        self.assertTrue(exists)


if __name__ == '__main__':
    unittest.main()
