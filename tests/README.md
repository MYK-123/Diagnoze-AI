# Unit Tests for Diagnoze-AI Project

This directory contains comprehensive unit tests for all modules in the Diagnoze-AI project with **100% code coverage**.

## Test Coverage

The test suite covers the following modules:

### Core Module (`core/`)
- **test_symptoms.py** - Tests for Symptom and Symptoms classes with database operations
- **test_disease.py** - Tests for Disease and Diseases classes with severity ranking
- **test_disease_symptoms_relation.py** - Tests for disease-symptom relationship management
- **test_predictions.py** - Tests for Prediction and Predictions classes
- **test_symptoms_input.py** - Tests for SymptomInput collection and database operations
- **test_extracted_symptoms.py** - Tests for extracted symptoms with confidence scoring

### Content Module (`content/`)
- **test_educational_content.py** - Tests for EducationContent and verification management

### Auth Module (`auth/`)
- **test_users.py** - Tests for User entity and authentication functions
- **test_sessions.py** - Tests for session creation, validation, and destruction
- **test_login.py** - Tests for login flow and user management

### Database Module (`db/`)
- **test_database.py** - Tests for database path functions and operations

## Running Tests

### Run all tests with coverage report:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_symptoms.py
```

### Run tests matching a pattern:
```bash
pytest tests/ -k "test_symptom"
```

### Run tests with verbose output:
```bash
pytest -v
```

### Generate HTML coverage report:
```bash
pytest --cov=core --cov=auth --cov=content --cov=db --cov-report=html
```

The HTML report will be generated in `htmlcov/index.html`

## Test Structure

Each test file follows this structure:

1. **Entity Tests** - Test class initialization, getters, and methods
2. **Collection Tests** - Test collection operations (add, filter, iterate)
3. **Database Tests** - Test database operations with mocked connections
4. **Exception Tests** - Test error handling and edge cases

## Code Coverage

All tests are designed to achieve 100% code coverage across:
- `core/` module - Core business logic
- `auth/` module - Authentication and user management
- `content/` module - Educational content management
- `db/` module - Database utilities

### Coverage Requirements

- **Minimum coverage**: 100%
- **Report formats**: HTML, Terminal (missing lines), XML

The `pytest.ini` configuration file sets `--cov-fail-under=100` to ensure the test suite fails if coverage drops below 100%.

## Mocking Strategy

Tests use `unittest.mock` to:
- Mock database connections and cursors
- Avoid actual database operations
- Test error handling scenarios
- Isolate units for true unit testing

## Test Naming Conventions

- `test_*` - All test functions start with `test_`
- `Test*` - All test classes start with `Test`
- Descriptive names indicate what is being tested

Example:
- `test_symptom_init` - Tests Symptom initialization
- `test_symptoms_add_duplicate` - Tests adding duplicate items
- `test_load_all_symptoms_exception` - Tests exception handling

## Dependencies

Required packages:
- `pytest` - Test framework
- `pytest-cov` - Coverage plugin
- `unittest.mock` - Built-in mocking library

These are already in `requirements.txt`.

## Notes

- All database operations are mocked to avoid side effects
- Tests are isolated and can run in any order
- Each test is independent and doesn't rely on other tests
- All edge cases and error scenarios are covered
