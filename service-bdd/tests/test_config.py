"""Tests for config module."""

import os

import pytest


class TestSettings:
    """Tests for Settings class."""

    def test_settings_default_values(self):
        """Settings should have default values."""
        from config import Settings

        settings = Settings()
        assert settings.database_host is not None
        assert settings.database_port == 5432
        assert settings.database_name is not None
        assert settings.database_user is not None
        assert settings.database_password is not None

    def test_settings_database_url_property(self):
        """Settings should generate correct database URL."""
        from config import Settings

        settings = Settings()
        url = settings.database_url
        assert url.startswith("postgresql://")
        assert settings.database_host in url
        assert str(settings.database_port) in url
        assert settings.database_name in url

    def test_settings_from_environment(self, monkeypatch):
        """Settings should read from environment variables."""
        monkeypatch.setenv("DATABASE_HOST", "testhost")
        monkeypatch.setenv("DATABASE_PORT", "5433")
        monkeypatch.setenv("DATABASE_NAME", "testdb")
        monkeypatch.setenv("DATABASE_USER", "testuser")
        monkeypatch.setenv("DATABASE_PASSWORD", "testpass")

        # Need to reimport to get new values
        import importlib

        import config

        importlib.reload(config)

        assert config.settings.database_host == "testhost"
        assert config.settings.database_port == 5433
        assert config.settings.database_name == "testdb"
