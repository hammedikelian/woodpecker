import logging
from typing import Any, Dict, List, Optional

import httpx
from config import settings

logger = logging.getLogger(__name__)


class BddClient:
    """HTTP client for communicating with the service-bdd."""

    def __init__(self):
        self.base_url = settings.service_bdd_url
        self.timeout = 10.0

    async def get_all_musiques(self) -> List[Dict[str, Any]]:
        """Fetch all musiques from the database service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/musiques")
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch musiques: {e}")
            raise

    async def get_musique_by_id(self, musique_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a specific musique by ID."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/musiques/{musique_id}")
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch musique {musique_id}: {e}")
            raise

    async def search_musiques(self, query: str) -> List[Dict[str, Any]]:
        """Search musiques by query."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/musiques/search", params={"q": query})
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to search musiques: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if the database service is healthy."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                data = response.json()
                return data.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
