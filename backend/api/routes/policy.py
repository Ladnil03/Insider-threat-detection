"""Policy endpoint — returns triggered policy violations for a user/activity."""

from fastapi import APIRouter

router = APIRouter(prefix="/policy-violations", tags=["policy"])


@router.get("/")
async def get_policy_violations(user_id: str = None):
    """List policy violations, optionally filtered by user."""
    raise NotImplementedError("Week 8 — implement policy endpoint.")
