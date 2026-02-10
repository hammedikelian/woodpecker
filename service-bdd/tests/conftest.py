"""Pytest configuration and fixtures for service-bdd tests."""

import os
import sys

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Reset environment variables for each test."""
    # Set default test environment
    monkeypatch.setenv("DATABASE_HOST", "localhost")
    monkeypatch.setenv("DATABASE_PORT", "5432")
    monkeypatch.setenv("DATABASE_NAME", "testdb")
    monkeypatch.setenv("DATABASE_USER", "testuser")
    monkeypatch.setenv("DATABASE_PASSWORD", "testpass")
