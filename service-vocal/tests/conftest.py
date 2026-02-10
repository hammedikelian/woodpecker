"""Pytest configuration and fixtures for service-vocal tests."""

import os
import sys

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Reset environment variables for each test."""
    # Set default test environment
    monkeypatch.setenv("SERVICE_BDD_URL", "http://localhost:5002")
    monkeypatch.setenv("VOSK_MODEL_PATH", "vosk-model-small-fr-0.22")
    monkeypatch.setenv("FUZZY_THRESHOLD", "70")


@pytest.fixture
def sample_musique():
    """Sample musique data for testing."""
    return {
        "id": 1,
        "titre": "Bohemian Rhapsody",
        "artiste": "Queen",
        "album": "A Night at the Opera",
        "duree_secondes": 354,
        "fichier_audio": "bohemian.mp3",
        "fichier_cover": "queen_cover.jpg",
    }


@pytest.fixture
def sample_musiques():
    """Sample music catalog for testing."""
    return [
        {
            "id": 1,
            "titre": "Bohemian Rhapsody",
            "artiste": "Queen",
            "album": "A Night at the Opera",
        },
        {
            "id": 2,
            "titre": "Billie Jean",
            "artiste": "Michael Jackson",
            "album": "Thriller",
        },
        {
            "id": 3,
            "titre": "Hotel California",
            "artiste": "Eagles",
            "album": "Hotel California",
        },
    ]
