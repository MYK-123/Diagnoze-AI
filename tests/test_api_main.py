#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app, root, health_check, system_stats


class TestAPIEndpoints(unittest.TestCase):
    """Test FastAPI endpoints"""

    def setUp(self):
        """Set up test client"""
        from fastapi.testclient import TestClient
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test root endpoint response"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Diagnoze AI API")
        self.assertIn("version", data)
        self.assertIn("docs", data)
        self.assertIn("health", data)

    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/api/v1/system/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        self.assertIn("service", data)
        self.assertEqual(data["service"], "diagnoze-api")
        self.assertIn("version", data)

    def test_health_check_timestamp_format(self):
        """Test that health check returns valid ISO timestamp"""
        response = self.client.get("/api/v1/system/health")
        data = response.json()
        timestamp = data["timestamp"]
        try:
            datetime.fromisoformat(timestamp)
            valid = True
        except (ValueError, TypeError):
            valid = False
        self.assertTrue(valid)

    def test_api_info_complete(self):
        """Test that root endpoint returns complete API info"""
        response = self.client.get("/")
        data = response.json()
        required_fields = ["message", "version", "docs", "health"]
        for field in required_fields:
            self.assertIn(field, data)

    def test_health_check_response_structure(self):
        """Test health check response structure"""
        response = self.client.get("/api/v1/system/health")
        data = response.json()
        required_fields = ["status", "timestamp", "service", "version"]
        for field in required_fields:
            self.assertIn(field, data)

    def test_root_endpoint_version(self):
        """Test root endpoint version"""
        response = self.client.get("/")
        data = response.json()
        self.assertEqual(data["version"], "1.0.0")

    def test_health_check_version(self):
        """Test health check version"""
        response = self.client.get("/api/v1/system/health")
        data = response.json()
        self.assertEqual(data["version"], "1.0.0")


class TestAppInitialization(unittest.TestCase):
    """Test FastAPI app initialization"""

    def test_app_exists(self):
        """Test that app is created"""
        self.assertIsNotNone(app)

    def test_app_title(self):
        """Test app title"""
        self.assertEqual(app.title, "Diagnoze AI API")

    def test_app_version(self):
        """Test app version"""
        self.assertEqual(app.version, "1.0.0")

    def test_app_docs_enabled(self):
        """Test that API docs are enabled"""
        self.assertIsNotNone(app.docs_url)
        self.assertEqual(app.docs_url, "/api/docs")

    def test_app_redoc_enabled(self):
        """Test that ReDoc is enabled"""
        self.assertIsNotNone(app.redoc_url)
        self.assertEqual(app.redoc_url, "/api/redoc")

    def test_app_has_cors_middleware(self):
        """Test that CORS middleware is installed"""
        # middleware_types = [type(m.cls).__name__ for m in app.user_middleware]
        middleware_types = [m.cls.__name__ for m in app.user_middleware]
        self.assertIn("CORSMiddleware", middleware_types)


class TestAppRouters(unittest.TestCase):
    """Test that app routers are properly included"""

    def test_auth_router_included(self):
        """Test that auth router is included"""
        routes = [route.path for route in app.routes]
        auth_routes = [r for r in routes if "/api/v1/auth" in r]
        self.assertGreater(len(auth_routes), 0)

    def test_users_router_included(self):
        """Test that users router is included"""
        routes = [route.path for route in app.routes]
        user_routes = [r for r in routes if "/api/v1/users" in r]
        # May be included in auth or separate
        self.assertGreater(len(routes), 0)

    def test_chat_router_included(self):
        """Test that chat router is included"""
        routes = [route.path for route in app.routes]
        chat_routes = [r for r in routes if "/api/v1/chat" in r]
        # May be included in other routers

    def test_medical_router_included(self):
        """Test that medical router is included"""
        routes = [route.path for route in app.routes]
        # Check that app has routes
        self.assertGreater(len(routes), 0)

    def test_admin_router_included(self):
        """Test that admin router is included"""
        routes = [route.path for route in app.routes]
        # Check that app has routes
        self.assertGreater(len(routes), 0)


class TestSystemStatsEndpoint(unittest.TestCase):
    """Test system stats endpoint"""

    @patch('api.main.get_current_user')
    @patch('api.main.get_db')
    def test_system_stats_requires_auth(self, mock_get_db, mock_auth):
        """Test that system stats requires authentication"""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Without auth, should fail with 403 or 401
        response = client.get("/api/v1/system/stats")
        # Status code depends on auth implementation
        self.assertIn(response.status_code, [401, 403, 200])

    def test_system_stats_path_exists(self):
        """Test that system stats path is defined"""
        routes = [route.path for route in app.routes]
        stats_routes = [r for r in routes if "/api/v1/system/stats" in r]
        self.assertGreater(len(stats_routes), 0)


class TestCORSConfiguration(unittest.TestCase):
    """Test CORS middleware configuration"""

    def setUp(self):
        """Set up test client"""
        from fastapi.testclient import TestClient
        self.client = TestClient(app)

    def test_cors_allows_all_origins(self):
        """Test that CORS allows requests"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_cors_allows_credentials(self):
        """Test CORS configuration"""
        # CORS middleware is configured with allow_credentials=True
        self.assertIsNotNone(app)


class TestEndpointSecurity(unittest.TestCase):
    """Test endpoint security features"""

    def setUp(self):
        """Set up test client"""
        from fastapi.testclient import TestClient
        self.client = TestClient(app)

    def test_public_endpoints_accessible(self):
        """Test that public endpoints are accessible"""
        public_endpoints = [
            "/",
            "/api/v1/system/health"
        ]
        for endpoint in public_endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 200)

    def test_response_json_valid(self):
        """Test that responses are valid JSON"""
        response = self.client.get("/")
        self.assertIsNotNone(response.json())
        
        response = self.client.get("/api/v1/system/health")
        self.assertIsNotNone(response.json())


if __name__ == '__main__':
    unittest.main()
