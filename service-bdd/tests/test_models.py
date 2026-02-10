"""Tests for models module."""

import pytest


class TestMusiqueModels:
    """Tests for Musique Pydantic models."""

    def test_musique_base_creation(self):
        """MusiqueBase should be created with required fields."""
        from models.musique import MusiqueBase

        musique = MusiqueBase(
            titre="Bohemian Rhapsody",
            artiste="Queen",
            duree_secondes=354,
            fichier_audio="bohemian.mp3",
        )
        assert musique.titre == "Bohemian Rhapsody"
        assert musique.artiste == "Queen"
        assert musique.duree_secondes == 354
        assert musique.fichier_audio == "bohemian.mp3"
        assert musique.album is None
        assert musique.fichier_cover is None

    def test_musique_base_with_optional_fields(self):
        """MusiqueBase should accept optional fields."""
        from models.musique import MusiqueBase

        musique = MusiqueBase(
            titre="Bohemian Rhapsody",
            artiste="Queen",
            album="A Night at the Opera",
            duree_secondes=354,
            fichier_audio="bohemian.mp3",
            fichier_cover="queen_cover.jpg",
        )
        assert musique.album == "A Night at the Opera"
        assert musique.fichier_cover == "queen_cover.jpg"

    def test_musique_create(self):
        """MusiqueCreate should inherit from MusiqueBase."""
        from models.musique import MusiqueCreate

        musique = MusiqueCreate(
            titre="Test Song",
            artiste="Test Artist",
            duree_secondes=180,
            fichier_audio="test.mp3",
        )
        assert musique.titre == "Test Song"

    def test_musique_with_id(self):
        """Musique should have an id field."""
        from models.musique import Musique

        musique = Musique(
            id=1,
            titre="Test Song",
            artiste="Test Artist",
            duree_secondes=180,
            fichier_audio="test.mp3",
        )
        assert musique.id == 1
        assert musique.titre == "Test Song"

    def test_musique_response(self):
        """MusiqueResponse should have all fields."""
        from models.musique import MusiqueResponse

        response = MusiqueResponse(
            id=1,
            titre="Test Song",
            artiste="Test Artist",
            album="Test Album",
            duree_secondes=180,
            fichier_audio="test.mp3",
            fichier_cover="cover.jpg",
        )
        assert response.id == 1
        assert response.titre == "Test Song"
        assert response.artiste == "Test Artist"
        assert response.album == "Test Album"

    def test_musique_response_optional_null(self):
        """MusiqueResponse should accept None for optional fields."""
        from models.musique import MusiqueResponse

        response = MusiqueResponse(
            id=1,
            titre="Test Song",
            artiste="Test Artist",
            album=None,
            duree_secondes=180,
            fichier_audio="test.mp3",
            fichier_cover=None,
        )
        assert response.album is None
        assert response.fichier_cover is None

    def test_musique_base_validation_error(self):
        """MusiqueBase should raise error for missing required fields."""
        from models.musique import MusiqueBase
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            MusiqueBase(titre="Test")  # Missing required fields

    def test_musique_duree_must_be_int(self):
        """duree_secondes should be an integer."""
        from models.musique import MusiqueBase

        musique = MusiqueBase(
            titre="Test",
            artiste="Artist",
            duree_secondes=180,
            fichier_audio="test.mp3",
        )
        assert isinstance(musique.duree_secondes, int)
