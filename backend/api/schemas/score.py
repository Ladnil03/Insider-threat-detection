"""Pydantic Schemas for Activity Scoring Endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ScoreRequest(BaseModel):
    """Payload for submitting user activity telemetry to be scored."""

    user_id: str = Field(..., description="Target employee user ID (e.g. ACM2278)")
    date_day: Optional[str] = Field(
        None, description="Activity date string (YYYY-MM-DD)"
    )
    user_role: Optional[str] = Field(
        None, description="Corporate role / privilege level"
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary of activity telemetry features (counts, rolling stats, deviations)",
    )


class PolicyActionSummary(BaseModel):
    """Summary of triggered automated policy actions."""

    rule_id: str
    rule_name: str
    severity: str
    action: str
    description: Optional[str] = None


class ScoreResponse(BaseModel):
    """Complete scoring breakdown response for a scored activity record."""

    activity_id: int
    user_id: str
    prism_score: float
    airs_score: float
    ensemble_score: float
    risk_level: str
    timestamp: datetime
    triggered_policies: List[PolicyActionSummary] = Field(default_factory=list)
