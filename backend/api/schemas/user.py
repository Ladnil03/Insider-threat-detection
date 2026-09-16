"""Pydantic Schemas for User History and Summary Endpoints."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from api.schemas.policy import PolicyViolationResponse


class UserActivityHistoryItem(BaseModel):
    """Timeline entry for user activity and historical scoring."""

    activity_id: int
    date_day: Optional[str] = None
    timestamp: datetime
    prism_score: float
    airs_score: float
    ensemble_score: float
    risk_level: str
    metrics: Dict[str, Any]


class UserHistoryResponse(BaseModel):
    """Complete user history response including timeline and policy alerts."""

    user_id: str
    user_name: str
    role: str
    department: str
    current_risk_score: float
    current_risk_level: str
    history: List[UserActivityHistoryItem]
    policy_violations: List[PolicyViolationResponse]


class UserSummaryResponse(BaseModel):
    """Summary item for the user risk overview directory."""

    user_id: str
    user_name: str
    role: str
    department: str
    latest_score: float
    risk_level: str
    latest_activity_date: Optional[str] = None
    violation_count: int = 0
