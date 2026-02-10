"""Tests for config module."""

import pytest


class TestSettings:
    """Tests for Settings class."""

    def test_settings_default_values(self):
        """Settings should have default values."""
        from config import Settings

        settings = Settings()
        assert settings.service_bdd_url is not None
        assert settings.vosk_model_path is not None
        assert settings.fuzzy_threshold is not None

    def test_settings_fuzzy_threshold_is_int(self):
        """fuzzy_threshold should be an integer."""
        from config import Settings

        settings = Settings()
        assert isinstance(settings.fuzzy_threshold, int)

    def test_settings_fuzzy_threshold_range(self):
        """fuzzy_threshold should be between 0 and 100."""
        from config import Settings

        settings = Settings()
        assert 0 <= settings.fuzzy_threshold <= 100

    def test_settings_service_bdd_url_format(self):
        """service_bdd_url should be a valid URL."""
        from config import Settings

        settings = Settings()
        assert settings.service_bdd_url.startswith("http")

    def test_settings_from_environment(self, monkeypatch):
        """Settings should read from environment variables."""
        monkeypatch.setenv("SERVICE_BDD_URL", "http://testhost:5000")
        monkeypatch.setenv("VOSK_MODEL_PATH", "test-model")
        monkeypatch.setenv("FUZZY_THRESHOLD", "80")

        # Reimport to get new values
        import importlib

        import config

        importlib.reload(config)

        assert config.settings.service_bdd_url == "http://testhost:5000"
        assert config.settings.vosk_model_path == "test-model"
        assert config.settings.fuzzy_threshold == 80

    def test_settings_instance_exists(self):
        """Global settings instance should exist."""
        from config import settings

        assert settings is not None
