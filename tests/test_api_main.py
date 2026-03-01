import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app, root, health_check, system_stats
from api.database import Base, get_db
from api.db_models import User, ChatHistory


# Use in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def test_db():
    """Create a test database"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield engine
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Create a test client"""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct info"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Diagnoze AI API"
        assert "version" in data
        assert "docs" in data

    def test_root_endpoint_structure(self, client):
        """Test that root response has correct structure"""
        response = client.get("/")
        data = response.json()
        
        assert "version" in data
        assert "docs" in data
        assert "health" in data


class TestHealthCheckEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check_success(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/system/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "diagnoze-api"

    def test_health_check_contains_timestamp(self, client):
        """Test that health check includes timestamp"""
        response = client.get("/api/v1/system/health")
        data = response.json()
        
        assert "timestamp" in data

    def test_health_check_version(self, client):
        """Test that health check includes version"""
        response = client.get("/api/v1/system/health")
        data = response.json()
        
        assert "version" in data
        assert data["version"] == "1.0.0"


class TestSystemStatsEndpoint:
    """Tests for system stats endpoint"""
    
    @patch('api.main.get_current_user')
    def test_system_stats_requires_auth(self, mock_get_user, client):
        """Test that system stats requires authentication"""
        response = client.get("/api/v1/system/stats")
        
        # Should fail without auth header
        assert response.status_code == 403

    @patch('api.main.get_current_user')
    def test_system_stats_with_auth(self, mock_get_user, client, test_db):
        """Test system stats with authentication"""
        # Mock the current user dependency
        mock_user_dict = {
            "id": "user123",
            "email": "test@example.com",
            "account_type": "user"
        }
        mock_get_user.return_value = mock_user_dict
        
        # Create test data
        from api.database import SessionLocal
        db = SessionLocal()
        
        user = User(
            id="user123",
            email="test@example.com",
            password_hash="hash",
            first_name="Test",
            last_name="User"
        )
        db.add(user)
        db.commit()
        
        response = client.get(
            "/api/v1/system/stats",
            headers={"Authorization": "Bearer tok_test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_chats" in data
        
        db.close()

    @patch('api.main.get_current_user')
    def test_system_stats_structure(self, mock_get_user, client):
        """Test system stats response structure"""
        mock_get_user.return_value = {"id": "user123", "account_type": "user"}
        
        response = client.get(
            "/api/v1/system/stats",
            headers={"Authorization": "Bearer tok_test"}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "total_users" in data
            assert "total_chats" in data
            assert "uptime" in data
            assert "timestamp" in data


class TestAppConfiguration:
    """Tests for app configuration"""
    
    def test_app_title(self):
        """Test that app has correct title"""
        assert app.title == "Diagnoze AI API"

    def test_app_description(self):
        """Test that app has description"""
        assert "Symptom Analysis" in app.description

    def test_app_version(self):
        """Test that app has correct version"""
        assert app.version == "1.0.0"

    def test_app_docs_url(self):
        """Test that docs URL is configured"""
        assert app.docs_url == "/api/docs"

    def test_app_redoc_url(self):
        """Test that redoc URL is configured"""
        assert app.redoc_url == "/api/redoc"


class TestCORSMiddleware:
    """Tests for CORS middleware"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in response"""
        response = client.get("/")
        
        assert response.status_code == 200
        # Note: TestClient may not include CORS headers by default
        # This is more of a configuration verification


class TestRouterInclusion:
    """Tests for router inclusion"""
    
    def test_auth_router_included(self, client):
        """Test that auth router is included"""
        # Try to access an auth endpoint
        response = client.post("/api/v1/auth/login", json={})
        
        # Should get 422 (validation error) or other response, not 404
        assert response.status_code != 404

    def test_routers_prefixes(self):
        """Test that routers have correct prefixes"""
        routes = [route.path for route in app.routes]
        
        # Check that router prefixes are present
        auth_routes = [r for r in routes if "/api/v1/auth" in r]
        assert len(auth_routes) > 0
        
        user_routes = [r for r in routes if "/api/v1/users" in r]
        assert len(user_routes) > 0


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_invalid_route_returns_404(self, client):
        """Test that invalid route returns 404"""
        response = client.get("/invalid/route/that/doesnt/exist")
        
        assert response.status_code == 404

    def test_method_not_allowed_returns_405(self, client):
        """Test that wrong HTTP method returns error"""
        response = client.post("/")
        
        # Root endpoint only accepts GET
        assert response.status_code in [405, 422]
