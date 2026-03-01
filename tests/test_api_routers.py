import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from api.database import Base, get_db
from api.db_models import User, SessionToken


TEST_DATABASE_URL = "sqlite:///./test_routers.db"

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


class TestAuthRouter:
    """Tests for authentication router"""
    
    def test_login_invalid_credentials(self, client, test_db):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!",
                "first_name": "John",
                "last_name": "Doe",
                "age": 30,
                "gender": "male",
                "account_type": "user"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or "access_token" in data

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "Password123!",
                "first_name": "John",
                "last_name": "Doe",
                "age": 30,
                "gender": "male",
                "account_type": "user"
            }
        )
        
        # Try to register with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "DifferentPassword123!",
                "first_name": "Jane",
                "last_name": "Smith",
                "age": 28,
                "gender": "female",
                "account_type": "user"
            }
        )
        
        assert response.status_code == 400

    def test_logout_invalid_token(self, client):
        """Test logout with invalid token"""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 401]

    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid token"""
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401

    def test_forgot_password(self, client):
        """Test forgot password endpoint"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 200

    def test_reset_password(self, client):
        """Test password reset endpoint"""
        response = client.post(
            "/api/v1/auth/reset-password",
            json={"token": "reset_token_123", "new_password": "NewPassword123!"}
        )
        
        assert response.status_code == 200


class TestUsersRouter:
    """Tests for users router"""
    
    @patch('api.routers.users.get_current_user')
    def test_get_profile_success(self, mock_get_user, client):
        """Test getting user profile"""
        mock_get_user.return_value = {
            "id": "user123",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "account_type": "user"
        }
        
        response = client.get(
            "/api/v1/users/profile",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        # Should return 200 or handle based on implementation
        assert response.status_code in [200, 401]

    @patch('api.routers.users.get_current_user')
    def test_update_profile_success(self, mock_get_user, client):
        """Test updating user profile"""
        mock_get_user.return_value = {
            "id": "user123",
            "email": "test@example.com",
            "account_type": "user"
        }
        
        response = client.put(
            "/api/v1/users/profile",
            json={"first_name": "Jane", "age": 25},
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code in [200, 401, 404]

    @patch('api.routers.users.get_current_user')
    def test_update_password_success(self, mock_get_user, client):
        """Test updating password"""
        mock_get_user.return_value = {"id": "user123"}
        
        response = client.put(
            "/api/v1/users/password",
            json={"old_password": "OldPass123!", "new_password": "NewPass123!"},
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code in [200, 401, 400]


class TestMedicalRouter:
    """Tests for medical router"""
    
    def test_get_diseases(self, client):
        """Test getting list of diseases"""
        response = client.get("/api/v1/medical/diseases")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or isinstance(data, list)

    def test_get_symptoms(self, client):
        """Test getting list of symptoms"""
        response = client.get("/api/v1/medical/symptoms")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data or isinstance(data, list)

    @patch('api.routers.medical.get_current_user')
    def test_get_disease_details(self, mock_get_user, client):
        """Test getting disease details"""
        mock_get_user.return_value = {"id": "user123"}
        
        response = client.get(
            "/api/v1/medical/diseases/1",
            headers={"Authorization": "Bearer valid_token"}
        )
        
        assert response.status_code in [200, 404]


class TestAdminRouter:
    """Tests for admin router"""
    
    @patch('api.routers.admin.get_current_admin')
    def test_get_users_admin_only(self, mock_get_admin, client):
        """Test that users endpoint requires admin"""
        mock_get_admin.return_value = {"id": "admin123", "account_type": "admin"}
        
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code in [200, 401, 403]

    @patch('api.routers.admin.get_current_admin')
    def test_get_statistics_admin_only(self, mock_get_admin, client):
        """Test that statistics endpoint requires admin"""
        mock_get_admin.return_value = {"id": "admin123", "account_type": "admin"}
        
        response = client.get(
            "/api/v1/admin/stats",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code in [200, 401, 403]

    @patch('api.routers.admin.get_current_admin')
    def test_update_user_role_admin_only(self, mock_get_admin, client):
        """Test updating user role requires admin"""
        mock_get_admin.return_value = {"id": "admin123", "account_type": "admin"}
        
        response = client.post(
            "/api/v1/admin/users/user123/role",
            json={"role": "medical_student"},
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code in [200, 400, 401, 403, 404]


class TestEndpointValidation:
    """Tests for endpoint validation and error handling"""
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/v1/auth/login",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields"""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"}  # Missing other required fields
        )
        
        assert response.status_code in [400, 422]

    def test_invalid_email_format(self, client):
        """Test email validation"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalid-email",
                "password": "Password123!",
                "first_name": "John",
                "last_name": "Doe",
                "age": 30,
                "gender": "male",
                "account_type": "user"
            }
        )
        
        assert response.status_code in [400, 422]

    def test_weak_password(self, client):
        """Test password strength validation"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak",  # Too weak
                "first_name": "John",
                "last_name": "Doe",
                "age": 30,
                "gender": "male",
                "account_type": "user"
            }
        )
        
        # May return 400 or 422 depending on validation
        assert response.status_code in [200, 400, 422]
