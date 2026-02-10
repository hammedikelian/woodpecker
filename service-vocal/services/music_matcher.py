import logging
from typing import Any, Dict, List, Optional

from config import settings
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)


class MusicMatcher:
    """Service for fuzzy matching music queries against the music catalog."""

    def __init__(self):
        self.threshold = settings.fuzzy_threshold

    def find_best_match(
        self, query: str, musiques: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Find the best matching music for a given query.

        Args:
            query: The search query (music title, artist, etc.)
            musiques: List of music dictionaries from the database

        Returns:
            Best matching music dict or None if no good match found
        """
        if not query or not musiques:
            return None

        query_lower = query.lower().strip()
        logger.info(f"Finding match for query: '{query_lower}'")

        best_match = None
        best_score = 0

        for musique in musiques:
            # Calculate scores for different fields
            titre_score = fuzz.token_set_ratio(query_lower, musique["titre"].lower())
            artiste_score = fuzz.token_set_ratio(query_lower, musique["artiste"].lower())

            # Combined search: "artiste titre" or "titre artiste"
            combined1 = f"{musique['artiste']} {musique['titre']}".lower()
            combined2 = f"{musique['titre']} {musique['artiste']}".lower()
            combined_score = max(
                fuzz.token_set_ratio(query_lower, combined1),
                fuzz.token_set_ratio(query_lower, combined2),
            )

            # Album score (lower weight)
            album_score = 0
            if musique.get("album"):
                album_score = (
                    fuzz.token_set_ratio(query_lower, musique["album"].lower()) * 0.7
                )  # Lower weight for album

            # Take the best score
            score = max(titre_score, artiste_score, combined_score, album_score)

            logger.debug(
                f"Music '{musique['titre']}' by {musique['artiste']}: "
                f"titre={titre_score}, artiste={artiste_score}, "
                f"combined={combined_score}, album={album_score}, best={score}"
            )

            if score > best_score:
                best_score = score
                best_match = musique

        if best_match and best_score >= self.threshold:
            logger.info(
                f"Best match: '{best_match['titre']}' by {best_match['artiste']} "
                f"(score: {best_score})"
            )
            return best_match

        logger.info(f"No match found above threshold {self.threshold}")
        return None

    def find_matches(
        self, query: str, musiques: List[Dict[str, Any]], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find multiple matching musics for a query.

        Args:
            query: The search query
            musiques: List of music dictionaries
            limit: Maximum number of results

        Returns:
            List of matching music dicts sorted by score
        """
        if not query or not musiques:
            return []

        query_lower = query.lower().strip()
        scored_musiques = []

        for musique in musiques:
            titre_score = fuzz.token_set_ratio(query_lower, musique["titre"].lower())
            artiste_score = fuzz.token_set_ratio(query_lower, musique["artiste"].lower())
            combined = f"{musique['artiste']} {musique['titre']}".lower()
            combined_score = fuzz.token_set_ratio(query_lower, combined)

            score = max(titre_score, artiste_score, combined_score)

            if score >= self.threshold:
                scored_musiques.append((musique, score))

        # Sort by score descending
        scored_musiques.sort(key=lambda x: x[1], reverse=True)

        return [m[0] for m in scored_musiques[:limit]]
