"""Pydantic Schemas for Analyst Feedback Endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FeedbackCreateRequest(BaseModel):
    """Payload for analyst risk adjustment feedback submission."""

    activity_id: int = Field(..., description="Target activity record ID")
    user_id: str = Field(..., description="Target employee user ID")
    adjusted_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Analyst adjusted risk score between 0.0 and 1.0",
    )
    notes: Optional[str] = Field(
        None, description="Analyst rationale or investigation notes"
    )


class FeedbackResponse(BaseModel):
    """Response confirming feedback persistence and mathematical score blending."""

    feedback_id: int
    activity_id: int
    user_id: str
    original_score: float
    adjusted_score: float
    blended_score: float
    notes: Optional[str] = None
    retrain_threshold_reached: bool = False
    timestamp: datetime
