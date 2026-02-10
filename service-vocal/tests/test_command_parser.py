"""Tests for command parser module."""

import pytest
from services.command_parser import CommandParser, Intent


class TestIntent:
    """Tests for Intent enum."""

    def test_intent_values(self):
        """Intent enum should have all expected values."""
        assert Intent.PLAY.value == "PLAY"
        assert Intent.STOP.value == "STOP"
        assert Intent.PAUSE.value == "PAUSE"
        assert Intent.RESUME.value == "RESUME"
        assert Intent.NEXT.value == "NEXT"
        assert Intent.PREVIOUS.value == "PREVIOUS"
        assert Intent.UNKNOWN.value == "UNKNOWN"

    def test_intent_is_string_enum(self):
        """Intent should be a string enum."""
        assert isinstance(Intent.PLAY, str)
        assert Intent.PLAY == "PLAY"


class TestCommandParser:
    """Tests for CommandParser class."""

    @pytest.fixture
    def parser(self):
        """Create a CommandParser instance."""
        return CommandParser()

    # PLAY intent tests
    def test_parse_joue(self, parser):
        """Should parse 'joue' as PLAY."""
        intent, query = parser.parse("joue bohemian rhapsody")
        assert intent == Intent.PLAY

    def test_parse_mets(self, parser):
        """Should parse 'mets' as PLAY."""
        intent, query = parser.parse("mets du queen")
        assert intent == Intent.PLAY

    def test_parse_lance(self, parser):
        """Should parse 'lance' as PLAY."""
        intent, query = parser.parse("lance la musique")
        assert intent == Intent.PLAY

    def test_parse_je_veux_ecouter(self, parser):
        """Should parse 'je veux écouter' as PLAY."""
        intent, query = parser.parse("je veux écouter hotel california")
        assert intent == Intent.PLAY

    def test_parse_play(self, parser):
        """Should parse 'play' as PLAY."""
        intent, query = parser.parse("play billie jean")
        assert intent == Intent.PLAY

    # STOP intent tests
    def test_parse_stop(self, parser):
        """Should parse 'stop' as STOP."""
        intent, query = parser.parse("stop")
        assert intent == Intent.STOP

    def test_parse_arrete(self, parser):
        """Should parse 'arrête' as STOP."""
        intent, query = parser.parse("arrête la musique")
        assert intent == Intent.STOP

    def test_parse_coupe(self, parser):
        """Should parse 'coupe' as STOP."""
        intent, query = parser.parse("coupe")
        assert intent == Intent.STOP

    # PAUSE intent tests
    def test_parse_pause(self, parser):
        """Should parse 'pause' as PAUSE."""
        intent, query = parser.parse("pause")
        assert intent == Intent.PAUSE

    def test_parse_mets_en_pause(self, parser):
        """Should parse 'mets en pause' as PAUSE."""
        intent, query = parser.parse("mets en pause")
        assert intent == Intent.PAUSE

    # RESUME intent tests
    def test_parse_reprends(self, parser):
        """Should parse 'reprends' as RESUME."""
        intent, query = parser.parse("reprends")
        assert intent == Intent.RESUME

    def test_parse_continue(self, parser):
        """Should parse 'continue' as RESUME."""
        intent, query = parser.parse("continue")
        assert intent == Intent.RESUME

    # NEXT intent tests
    def test_parse_suivant(self, parser):
        """Should parse 'suivant' as NEXT."""
        intent, query = parser.parse("suivant")
        assert intent == Intent.NEXT

    def test_parse_skip(self, parser):
        """Should parse 'skip' as NEXT."""
        intent, query = parser.parse("skip")
        assert intent == Intent.NEXT

    def test_parse_next(self, parser):
        """Should parse 'next' as NEXT."""
        intent, query = parser.parse("next")
        assert intent == Intent.NEXT

    # PREVIOUS intent tests
    def test_parse_precedent(self, parser):
        """Should parse 'précédent' as PREVIOUS."""
        intent, query = parser.parse("précédent")
        assert intent == Intent.PREVIOUS

    def test_parse_reviens(self, parser):
        """Should parse 'reviens' as PREVIOUS."""
        intent, query = parser.parse("reviens")
        assert intent == Intent.PREVIOUS

    def test_parse_previous(self, parser):
        """Should parse 'previous' as PREVIOUS."""
        intent, query = parser.parse("previous")
        assert intent == Intent.PREVIOUS

    # UNKNOWN intent tests
    def test_parse_empty_string(self, parser):
        """Should return UNKNOWN for empty string."""
        intent, query = parser.parse("")
        assert intent == Intent.UNKNOWN

    def test_parse_none(self, parser):
        """Should return UNKNOWN for None."""
        intent, query = parser.parse(None)
        assert intent == Intent.UNKNOWN

    def test_parse_single_unknown_word(self, parser):
        """Should return UNKNOWN for single unknown word."""
        intent, query = parser.parse("xyz")
        assert intent == Intent.UNKNOWN

    # Music query extraction tests
    def test_extract_query_from_joue(self, parser):
        """Should extract music query from joue command."""
        intent, query = parser.parse("joue bohemian rhapsody")
        assert query is not None
        assert "bohemian" in query.lower()

    def test_extract_query_from_mets(self, parser):
        """Should extract artist name from mets command."""
        intent, query = parser.parse("mets queen")
        assert query is not None
        assert "queen" in query.lower()

    def test_extract_query_removes_command_words(self, parser):
        """Should remove command words from query."""
        intent, query = parser.parse("joue la musique de queen")
        assert query is not None
        assert "joue" not in query.lower()
        assert "la" not in query.lower()
        assert "musique" not in query.lower()
        assert "de" not in query.lower()

    def test_no_query_for_stop(self, parser):
        """Should not extract query for STOP intent."""
        intent, query = parser.parse("stop")
        assert intent == Intent.STOP
        assert query is None

    def test_case_insensitive(self, parser):
        """Parser should be case insensitive."""
        intent1, _ = parser.parse("JOUE queen")
        intent2, _ = parser.parse("joue queen")
        intent3, _ = parser.parse("Joue Queen")
        assert intent1 == Intent.PLAY
        assert intent2 == Intent.PLAY
        assert intent3 == Intent.PLAY

    def test_whitespace_handling(self, parser):
        """Parser should handle extra whitespace."""
        intent, query = parser.parse("  joue   bohemian   rhapsody  ")
        assert intent == Intent.PLAY
        assert query is not None
