#!/usr/bin/env python3

import pytest
import warnings
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure pytest
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )


# Fixtures for common test setup
@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary test database"""
    db_path = tmp_path / "test.db"
    return str(db_path)

# Ignoreing warnings
def pytest_sessionstart(session):
    warnings.filterwarnings(
        "ignore",
        message=".*builtin type SwigPy*.",
        category=DeprecationWarning
    )
