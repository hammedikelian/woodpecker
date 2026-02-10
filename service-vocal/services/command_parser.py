import logging
import re
from enum import Enum
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    PLAY = "PLAY"
    STOP = "STOP"
    PAUSE = "PAUSE"
    RESUME = "RESUME"
    NEXT = "NEXT"
    PREVIOUS = "PREVIOUS"
    UNKNOWN = "UNKNOWN"


class CommandParser:
    """Parser for voice commands to detect user intentions."""

    # Command patterns with their associated intents
    PATTERNS = {
        Intent.PLAY: [
            r"\b(joue|jouer)\b",
            r"\b(mets|mettre)\b",
            r"\b(lance|lancer)\b",
            r"\bje veux (écouter|ecouter)\b",
            r"\b(écouter|ecouter)\b",
            r"\bplay\b",
            r"\bfais jouer\b",
            r"\bpasse|passer\b.*\bmusique\b",
        ],
        Intent.STOP: [
            r"\bstop\b",
            r"\b(arrête|arrete|arrêter|arreter)\b",
            r"\bcoupe\b",
            r"\b(termine|terminer)\b",
            r"\bfin\b",
        ],
        Intent.PAUSE: [
            r"\bpause\b",
            r"\bmets en pause\b",
            r"\b(suspends|suspendre)\b",
        ],
        Intent.RESUME: [
            r"\b(reprends|reprendre)\b",
            r"\bcontinue\b",
            r"\b(relance|relancer)\b",
            r"\bplay\b(?!.*\b(musique|chanson|titre)\b)",
        ],
        Intent.NEXT: [
            r"\b(suivant|suivante)\b",
            r"\bpasse\b(?!.*\b(musique|chanson)\b)",
            r"\bskip\b",
            r"\bnext\b",
            r"\bprochaine?\b",
        ],
        Intent.PREVIOUS: [
            r"\b(précédent|precedent|précédente|precedente)\b",
            r"\b(reviens|revenir)\b",
            r"\bavant\b",
            r"\bprevious\b",
            r"\bback\b",
        ],
    }

    # Words to remove to extract the music query
    COMMAND_WORDS = [
        "joue",
        "jouer",
        "mets",
        "mettre",
        "lance",
        "lancer",
        "je",
        "veux",
        "écouter",
        "ecouter",
        "la",
        "le",
        "les",
        "un",
        "une",
        "de",
        "du",
        "des",
        "musique",
        "chanson",
        "titre",
        "morceau",
        "s'il",
        "te",
        "plait",
        "plaît",
        "play",
        "fais",
        "passe",
        "passer",
        "me",
        "moi",
    ]

    def parse(self, text: str) -> Tuple[Intent, Optional[str]]:
        """
        Parse a voice command to extract intent and music query.

        Args:
            text: Transcribed voice command

        Returns:
            Tuple of (Intent, music_query or None)
        """
        if not text:
            return Intent.UNKNOWN, None

        text_lower = text.lower().strip()
        logger.info(f"Parsing command: '{text_lower}'")

        # Detect intent
        detected_intent = self._detect_intent(text_lower)
        logger.info(f"Detected intent: {detected_intent}")

        # Extract music query for PLAY intent
        music_query = None
        if detected_intent == Intent.PLAY:
            music_query = self._extract_music_query(text_lower)
            logger.info(f"Extracted music query: '{music_query}'")

        return detected_intent, music_query

    def _detect_intent(self, text: str) -> Intent:
        """Detect the user's intent from the command."""
        # Check each intent's patterns
        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Special case: "passe" could be PLAY or NEXT
                    if intent == Intent.NEXT and "passe" in pattern:
                        # If followed by music-related words, it's PLAY
                        if re.search(r"passe.*\b(musique|chanson|titre)\b", text):
                            continue
                    return intent

        # Default to PLAY if text contains potential music name
        if len(text.split()) > 1:
            return Intent.PLAY

        return Intent.UNKNOWN

    def _extract_music_query(self, text: str) -> Optional[str]:
        """Extract the music name/query from the command."""
        # Remove command words
        words = text.split()
        filtered_words = []

        for word in words:
            # Clean word of punctuation
            clean_word = re.sub(r"[^\w\s]", "", word)
            if clean_word and clean_word.lower() not in self.COMMAND_WORDS:
                filtered_words.append(word)

        query = " ".join(filtered_words).strip()

        # If query is empty or too short, return None
        if not query or len(query) < 2:
            return None

        return query
