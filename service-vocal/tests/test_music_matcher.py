"""Tests for music matcher module."""

import pytest
from services.music_matcher import MusicMatcher


class TestMusicMatcher:
    """Tests for MusicMatcher class."""

    @pytest.fixture
    def matcher(self):
        """Create a MusicMatcher instance."""
        return MusicMatcher()

    @pytest.fixture
    def sample_musiques(self):
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
            {
                "id": 4,
                "titre": "Stairway to Heaven",
                "artiste": "Led Zeppelin",
                "album": "Led Zeppelin IV",
            },
            {
                "id": 5,
                "titre": "Imagine",
                "artiste": "John Lennon",
                "album": "Imagine",
            },
        ]

    # find_best_match tests
    def test_find_exact_title_match(self, matcher, sample_musiques):
        """Should find exact title match."""
        result = matcher.find_best_match("Bohemian Rhapsody", sample_musiques)
        assert result is not None
        assert result["titre"] == "Bohemian Rhapsody"

    def test_find_partial_title_match(self, matcher, sample_musiques):
        """Should find partial title match."""
        result = matcher.find_best_match("bohemian", sample_musiques)
        assert result is not None
        assert result["titre"] == "Bohemian Rhapsody"

    def test_find_artist_match(self, matcher, sample_musiques):
        """Should find match by artist name."""
        result = matcher.find_best_match("Queen", sample_musiques)
        assert result is not None
        assert result["artiste"] == "Queen"

    def test_find_combined_match(self, matcher, sample_musiques):
        """Should find match with artist and title combined."""
        result = matcher.find_best_match("Queen Bohemian", sample_musiques)
        assert result is not None
        assert result["artiste"] == "Queen"

    def test_case_insensitive_match(self, matcher, sample_musiques):
        """Should match regardless of case."""
        result = matcher.find_best_match("BOHEMIAN RHAPSODY", sample_musiques)
        assert result is not None
        assert result["titre"] == "Bohemian Rhapsody"

    def test_no_match_below_threshold(self, matcher, sample_musiques):
        """Should return None if no match above threshold."""
        result = matcher.find_best_match("xyz random text", sample_musiques)
        assert result is None

    def test_empty_query(self, matcher, sample_musiques):
        """Should return None for empty query."""
        result = matcher.find_best_match("", sample_musiques)
        assert result is None

    def test_none_query(self, matcher, sample_musiques):
        """Should return None for None query."""
        result = matcher.find_best_match(None, sample_musiques)
        assert result is None

    def test_empty_musiques_list(self, matcher):
        """Should return None for empty music list."""
        result = matcher.find_best_match("Queen", [])
        assert result is None

    def test_none_musiques_list(self, matcher):
        """Should return None for None music list."""
        result = matcher.find_best_match("Queen", None)
        assert result is None

    def test_whitespace_query(self, matcher, sample_musiques):
        """Should handle whitespace in query."""
        result = matcher.find_best_match("  Queen  ", sample_musiques)
        assert result is not None
        assert result["artiste"] == "Queen"

    # find_matches tests
    def test_find_matches_returns_list(self, matcher, sample_musiques):
        """Should return a list of matches."""
        results = matcher.find_matches("rock", sample_musiques)
        assert isinstance(results, list)

    def test_find_matches_empty_query(self, matcher, sample_musiques):
        """Should return empty list for empty query."""
        results = matcher.find_matches("", sample_musiques)
        assert results == []

    def test_find_matches_none_query(self, matcher, sample_musiques):
        """Should return empty list for None query."""
        results = matcher.find_matches(None, sample_musiques)
        assert results == []

    def test_find_matches_empty_musiques(self, matcher):
        """Should return empty list for empty music list."""
        results = matcher.find_matches("Queen", [])
        assert results == []

    def test_find_matches_respects_limit(self, matcher, sample_musiques):
        """Should respect the limit parameter."""
        # Add more similar items
        musiques = sample_musiques + [
            {"id": 6, "titre": "Queen Song 1", "artiste": "Queen", "album": "Album"},
            {"id": 7, "titre": "Queen Song 2", "artiste": "Queen", "album": "Album"},
        ]
        results = matcher.find_matches("Queen", musiques, limit=2)
        assert len(results) <= 2

    def test_find_matches_sorted_by_score(self, matcher, sample_musiques):
        """Results should be sorted by match score."""
        results = matcher.find_matches("Bohemian Rhapsody Queen", sample_musiques)
        if len(results) > 0:
            # First result should be the best match
            assert results[0]["titre"] == "Bohemian Rhapsody"


class TestMusicMatcherThreshold:
    """Tests for MusicMatcher threshold behavior."""

    def test_default_threshold(self):
        """Should have a default threshold."""
        matcher = MusicMatcher()
        assert matcher.threshold is not None
        assert isinstance(matcher.threshold, int)
        assert matcher.threshold > 0
        assert matcher.threshold <= 100

    def test_threshold_affects_matching(self):
        """Threshold should affect what gets matched."""
        matcher = MusicMatcher()
        musiques = [{"id": 1, "titre": "ABC", "artiste": "XYZ", "album": "123"}]

        # Very different query should not match
        result = matcher.find_best_match("completely different", musiques)
        assert result is None
