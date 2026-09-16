"""Pydantic Schemas for Policy Violation Log Endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PolicyViolationResponse(BaseModel):
    """Schema for individual policy violation log event."""

    id: int
    activity_id: Optional[int] = None
    user_id: str
    rule_id: str
    rule_name: str
    severity: str
    action: str
    description: Optional[str] = None
    timestamp: datetime
