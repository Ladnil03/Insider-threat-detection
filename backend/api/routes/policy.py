"""Policy Engine Route Endpoint."""

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class PolicyViolation(BaseModel):
    user_id: str
    rule_id: str
    action_taken: str
    timestamp: str


@router.get("/policy-violations", response_model=List[PolicyViolation])
def get_policy_violations() -> List[PolicyViolation]:
    """Retrieves simulated automated policy violation actions.

    Returns:
        List of PolicyViolation objects.
    """
    return [
        PolicyViolation(
            user_id="USR-102",
            rule_id="RULE-USB-01",
            action_taken="SIMULATED_USB_BLOCK",
            timestamp="2026-07-28T12:00:00Z",
        )
    ]
