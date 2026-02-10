"""Tests for service-bdd API endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_200(self):
        """Root endpoint should return 200."""
        from app import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_service_info(self):
        """Root endpoint should return service info."""
        from app import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/")
        data = response.json()
        assert data["service"] == "service-bdd"
        assert "version" in data
        assert "endpoints" in data

    def test_root_contains_endpoints_list(self):
        """Root endpoint should list available endpoints."""
        from app import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/")
        data = response.json()
        assert "/health" in data["endpoints"]
        assert "/musiques" in data["endpoints"]


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_endpoint_exists(self):
        """Health endpoint should exist."""
        from app import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health")
        # Should return 200 even if DB is not connected (returns unhealthy status)
        assert response.status_code == 200

    def test_health_returns_status_field(self):
        """Health endpoint should return status field."""
        from app import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health")
        data = response.json()
        assert "status" in data

    @patch("app.get_connection")
    def test_health_healthy_when_db_connected(self, mock_conn):
        """Health should return healthy when DB is connected."""
        mock_conn.return_value = MagicMock()

        from app import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    @patch("app.get_connection")
    def test_health_unhealthy_when_db_error(self, mock_conn):
        """Health should return unhealthy when DB connection fails."""
        mock_conn.side_effect = Exception("Connection failed")

        from app import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "unhealthy"


class TestAppConfiguration:
    """Tests for app configuration."""

    def test_app_title(self):
        """App should have correct title."""
        from app import app

        assert app.title == "Service BDD - Music Voice App"

    def test_app_version(self):
        """App should have version."""
        from app import app

        assert app.version == "1.0.0"

    def test_cors_middleware_added(self):
        """App should have CORS middleware."""
        from app import app

        # Check that middleware is configured
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    def test_musiques_router_included(self):
        """App should include musiques router."""
        from app import app

        # Check that routes exist
        routes = [route.path for route in app.routes]
        assert any("/musiques" in route for route in routes)
