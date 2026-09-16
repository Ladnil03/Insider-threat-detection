"""Pydantic Schemas for Generic Activity Models."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ActivityCreateRequest(BaseModel):
    """Payload for creating a raw activity entry."""

    user_id: str
    date_day: Optional[str] = None
    metrics: Dict[str, Any] = {}


class ActivityResponse(BaseModel):
    """Response payload for an activity log record."""

    id: int
    user_id: str
    date_day: Optional[str] = None
    metrics: Dict[str, Any]
    created_at: datetime
