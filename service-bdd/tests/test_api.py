"""Tests for service-bdd API."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_returns_200(self):
        """Health endpoint should return 200."""
        # Import here to avoid database connection issues in CI
        from app import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self):
        """Health endpoint should return status field."""
        from app import app

        client = TestClient(app)
        response = client.get("/health")
        data = response.json()
        assert "status" in data


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_200(self):
        """Root endpoint should return 200."""
        from app import app

        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_service_info(self):
        """Root endpoint should return service info."""
        from app import app

        client = TestClient(app)
        response = client.get("/")
        data = response.json()
        assert data["service"] == "service-bdd"
        assert "version" in data
