"""Pydantic Schemas for LLM Threat Recommendation Endpoints."""

from typing import List, Optional

from pydantic import BaseModel, Field


class RiskDriver(BaseModel):
    """Specific risk driver extracted by LLM reasoning."""

    feature: str
    impact: str
    description: str


class RecommendationResponse(BaseModel):
    """Structured LLM analyst recommendation response."""

    activity_id: int
    user_id: str
    risk_score: float
    risk_level: str
    summary: str
    risk_drivers: List[RiskDriver] = Field(default_factory=list)
    recommended_action: str
    urgency: str
    model: Optional[str] = None
    provider: Optional[str] = None
    status: str = "success"
