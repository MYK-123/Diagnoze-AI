# Unit Testing Guide - Diagnoze AI

Welcome to the comprehensive unit testing documentation for the Diagnoze AI project. This guide provides everything you need to understand, run, and maintain the test suite.

## 📋 Quick Start

### Installation
```bash
# Navigate to project directory
cd "c:\Users\user\Desktop\MCA Project\Project\WebPages"

# Install test dependencies
pip install -r requirements.txt

# Verify pytest is installed
pytest --version
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Tests with Coverage
```bash
pytest tests/ -v --cov=api --cov-report=term-missing
```

## 📂 Test File Structure

```
tests/
├── test_api_main.py              (7 test classes, 20+ tests)
├── test_api_routers.py           (6 test classes, 22+ tests)
├── test_auth_db.py               (5 test classes, 18+ tests)
├── test_auth.py                  (7 test classes, 28+ tests)
├── test_chat_router.py           (7 test classes, 25+ tests)
├── test_core_functions.py        (10 test classes, 30+ tests)
├── test_db_models.py             (6 test classes, 28+ tests)
├── test_disease.py               (5 test classes, 30+ tests)
├── conftest.py                   (Shared fixtures and configuration)
├── pytest.ini                     (Pytest configuration)
├── TEST_SUMMARY.md               (Detailed test documentation)
└── README.md                      (This file)
```

## 🧪 Test Categories

### 1. API Tests (test_api_main.py, test_api_routers.py)
- **Total**: 42+ tests
- **Coverage**: API endpoints, routing, CORS, authentication
- **Focus**: HTTP status codes, response validation, error handling

**Key Tests:**
- Root endpoint (`/`)
- Health check (`/api/v1/system/health`)
- Authentication endpoints (`/api/v1/auth/*`)
- User management (`/api/v1/users/*`)
- Medical data (`/api/v1/medical/*`)
- Admin operations (`/api/v1/admin/*`)

### 2. Authentication Tests (test_auth_db.py, test_auth.py)
- **Total**: 46+ tests
- **Coverage**: Password hashing, token management, user operations
- **Focus**: Security, cryptography, session handling

**Key Tests:**
- PBKDF2 password hashing
- Password verification
- Session token generation
- User registration/login
- Role management
- Permission checks

### 3. Database Model Tests (test_db_models.py)
- **Total**: 28+ tests
- **Coverage**: SQLAlchemy models, serialization, relationships
- **Focus**: Data integrity, JSON handling, model methods

**Key Tests:**
- User model
- Session token model
- Chat session & messages
- Chat history
- JSON utilities
- Data serialization

### 4. Core Business Logic Tests (test_core_functions.py)
- **Total**: 30+ tests
- **Coverage**: Disease prediction, symptom analysis
- **Focus**: Algorithm correctness, probability calculations

**Key Tests:**
- Prediction algorithms
- Symptom extraction
- Disease ranking
- Educational content retrieval
- Prompt generation

### 5. Domain Entity Tests (test_disease.py)
- **Total**: 30+ tests
- **Coverage**: Disease objects, collections, caching
- **Focus**: Entity behavior, filtering, persistence

**Key Tests:**
- Disease creation and updates
- Disease collections
- Filtering operations
- Severity ranking
- Cache management

### 6. Chat Functionality Tests (test_chat_router.py)
- **Total**: 25+ tests
- **Coverage**: Chat sessions, messaging, predictions
- **Focus**: State management, response generation

**Key Tests:**
- Session creation
- Message handling
- AI response generation
- Prediction generation
- Session persistence

## 🚀 Running Tests

### Basic Commands

```bash
# Run all tests verbosely
pytest tests/ -v

# Run specific test file
pytest tests/test_auth_db.py -v

# Run specific test class
pytest tests/test_auth_db.py::TestHashPassword -v

# Run specific test method
pytest tests/test_auth_db.py::TestHashPassword::test_hash_password_creates_valid_hash -v

# Run tests matching pattern
pytest tests/ -k "auth" -v

# Run tests with short traceback
pytest tests/ --tb=short

# Stop on first failure
pytest tests/ -x
```

### Coverage Reports

```bash
# Terminal coverage report
pytest tests/ --cov=api --cov-report=term-missing

# HTML coverage report
pytest tests/ --cov=api --cov-report=html
# Open: htmlcov/index.html

# Coverage with multiple modules
pytest tests/ --cov=api --cov=auth --cov=core --cov-report=html
```

### Performance Testing

```bash
# Show slowest tests
pytest tests/ --durations=10

# Show test timings
pytest tests/ -v --durations=0

# Run tests in parallel (requires pytest-xdist)
pytest tests/ -n auto
```

## 🔍 Understanding Test Output

### Successful Test Run
```
tests/test_auth_db.py::TestHashPassword::test_hash_password_creates_valid_hash PASSED
```

### Failed Test Run
```
tests/test_auth_db.py::TestHashPassword::test_verify_incorrect_password FAILED

AssertionError: assert False == True
```

### Skipped Test
```
tests/test_example.py::test_feature_not_yet_implemented SKIPPED
```

## 📊 Test Coverage Goals

| Module | Target Coverage | Current Status |
|--------|-----------------|----------------|
| api/ | 85%+ | In Progress |
| auth/ | 90%+ | In Progress |
| core/ | 80%+ | In Progress |
| tests/ | 100% | ✅ Complete |

## 🛠️ Common Testing Scenarios

### Test a New Feature

1. **Create test file** (if new module):
```bash
# tests/test_new_feature.py
```

2. **Write tests first** (TDD approach):
```python
class TestNewFeature:
    def test_basic_functionality(self):
        # Arrange
        expected = "result"
        # Act
        result = new_feature()
        # Assert
        assert result == expected
```

3. **Run tests**:
```bash
pytest tests/test_new_feature.py -v
```

4. **Implement feature** to make tests pass

### Test Error Handling

```python
def test_invalid_input_raises_error(self):
    with pytest.raises(ValueError):
        function_with_validation("invalid input")
```

### Test with Mock Objects

```python
@patch('module.external_function')
def test_with_mock(self, mock_func):
    mock_func.return_value = "mocked result"
    result = function_that_calls_external()
    assert result == "mocked result"
    assert mock_func.called
```

## 🔐 Security Testing

Tests verify:
- ✅ Password hashing with PBKDF2
- ✅ Session token validation
- ✅ Admin authorization checks
- ✅ User permission validation
- ✅ Input validation and sanitization
- ✅ SQL injection prevention (SQLAlchemy)
- ✅ CORS configuration

## 🐛 Debugging Tests

### Verbose Output
```bash
pytest tests/test_auth_db.py::TestHashPassword::test_hash_password_creates_valid_hash -vv
```

### Show Print Statements
```bash
pytest tests/ -v -s
```

### Drop into Debugger on Failure
```bash
pytest tests/ --pdb
```

### Show Local Variables on Failure
```bash
pytest tests/ --showlocals
```

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=api --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 📝 Test File Template

Use this template when creating new test files:

```python
import pytest
from unittest.mock import Mock, MagicMock, patch

# Import the modules to test
from module_to_test import function_or_class


class TestFeatureName:
    """Tests for feature_name functionality"""
    
    def test_basic_operation(self):
        """Test that feature works correctly"""
        # Arrange
        input_data = "test"
        expected = "result"
        
        # Act
        result = function_or_class(input_data)
        
        # Assert
        assert result == expected
    
    def test_error_handling(self):
        """Test that feature handles errors"""
        with pytest.raises(ValueError):
            function_or_class("invalid")
    
    @patch('module_to_test.external_dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked external dependency"""
        mock_dep.return_value = "mocked"
        result = function_or_class("input")
        assert mock_dep.called
```

## 🔧 Fixture Guide

### Database Fixture
```python
@pytest.fixture
def test_db():
    """Provide test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
```

### User Fixture
```python
@pytest.fixture
def test_user(test_db):
    """Provide test user"""
    user = User(id="user1", email="test@example.com", ...)
    db.add(user)
    db.commit()
    return user
```

### Authentication Fixture
```python
@pytest.fixture
def auth_token(test_db):
    """Provide valid auth token"""
    user = User(...)
    session = SessionToken.new_token()
    return session.token
```

## 📚 Test Assertions

### Common Assertions
```python
assert x == y                    # Equality
assert x != y                    # Inequality
assert x > y                     # Greater than
assert x in list                 # Membership
assert callable(func)            # Callable check
assert isinstance(obj, Class)    # Type check
assert x is None                 # None check
```

### List/Dict Assertions
```python
assert len(items) == 3           # Length
assert item in items             # Containment
assert items[0] == expected      # Item access
assert d['key'] == value         # Dictionary access
```

### Exception Assertions
```python
with pytest.raises(ValueError):
    function_that_raises()

with pytest.raises(ValueError, match="error message"):
    function_that_raises()
```

## ⚙️ Configuration

### pytest.ini
```ini
[pytest]
testpaths = tests
addopts = --cov=api --cov-report=term-missing
pythonpath = .
markers =
    api: tests for the api
    backend: tests for the backend
```

### conftest.py
- Shared fixtures
- Test configuration
- Database setup
- Mock factories

## 🚨 Troubleshooting

### Import Errors
```bash
# Set Python path
set PYTHONPATH=%CD%
pytest tests/
```

### Database Lock Errors
```bash
# Clear cache
rmdir /s __pycache__ .pytest_cache
pytest tests/
```

### Fixture Scope Issues
```bash
# Show fixture details
pytest tests/ --setup-show -v
```

### Test Discovery Issues
```bash
# List all discovered tests
pytest tests/ --collect-only
```

## 📋 Pre-commit Checklist

Before committing code:

- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage acceptable: `pytest tests/ --cov=api`
- [ ] No lint errors: `flake8 api/` (optional)
- [ ] Code formatted: `black .` (optional)
- [ ] Tests added for new features
- [ ] Documentation updated
- [ ] No hardcoded credentials

## 🎓 Learning Resources

### Pytest Documentation
- https://docs.pytest.org/

### Testing Best Practices
- https://docs.python-guide.org/writing/tests/

### Mock Objects
- https://docs.python.org/3/library/unittest.mock.html

### FastAPI Testing
- https://fastapi.tiangolo.com/advanced/testing-dependencies/

## 🤝 Contributing Tests

1. Fork or branch
2. Write tests first (TDD)
3. Implement feature to pass tests
4. Ensure all tests pass
5. Submit PR with test coverage

## 📞 Support

For issues or questions:
1. Check TEST_SUMMARY.md for detailed documentation
2. Review similar test files for patterns
3. Run tests with `-vv` for verbose output
4. Use `--pdb` for interactive debugging

## 📅 Test Maintenance Schedule

- **Weekly**: Run full test suite
- **Before release**: 100% test pass rate required
- **Monthly**: Review and update test documentation
- **Quarterly**: Audit test coverage and refactor

---

**Last Updated**: March 1, 2026
**Total Tests**: 200+
**Test Files**: 8
**Coverage Target**: 85%+
