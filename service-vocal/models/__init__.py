from typing import Any, Dict, Optional

from pydantic import BaseModel


class RecognitionRequest(BaseModel):
    """Request model for audio recognition."""

    pass


class RecognitionResponse(BaseModel):
    """Response model for audio recognition."""

    success: bool
    transcript: Optional[str] = None
    intent: str
    musique: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confidence: Optional[float] = None
