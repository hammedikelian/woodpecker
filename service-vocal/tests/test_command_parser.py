"""Tests for command parser."""

import pytest
from services.command_parser import CommandParser, Intent


class TestCommandParser:
    """Tests for CommandParser class."""

    @pytest.fixture
    def parser(self):
        """Create a CommandParser instance."""
        return CommandParser()

    def test_parse_play_command(self, parser):
        """Should parse play commands correctly."""
        intent, query = parser.parse("joue bohemian rhapsody")
        assert intent == Intent.PLAY
        assert "bohemian" in query.lower()

    def test_parse_stop_command(self, parser):
        """Should parse stop commands correctly."""
        intent, query = parser.parse("stop")
        assert intent == Intent.STOP

    def test_parse_pause_command(self, parser):
        """Should parse pause commands correctly."""
        intent, query = parser.parse("pause")
        assert intent == Intent.PAUSE

    def test_parse_resume_command(self, parser):
        """Should parse resume commands correctly."""
        intent, query = parser.parse("reprends")
        assert intent == Intent.RESUME

    def test_parse_next_command(self, parser):
        """Should parse next commands correctly."""
        intent, query = parser.parse("suivant")
        assert intent == Intent.NEXT

    def test_parse_previous_command(self, parser):
        """Should parse previous commands correctly."""
        intent, query = parser.parse("precedent")
        assert intent == Intent.PREVIOUS

    def test_parse_unknown_command(self, parser):
        """Should return UNKNOWN for unrecognized commands."""
        intent, query = parser.parse("blablabla random text")
        assert intent == Intent.UNKNOWN


class TestMusicMatcher:
    """Tests for MusicMatcher class."""

    def test_import_music_matcher(self):
        """Should be able to import MusicMatcher."""
        from services.music_matcher import MusicMatcher

        matcher = MusicMatcher()
        assert matcher is not None
