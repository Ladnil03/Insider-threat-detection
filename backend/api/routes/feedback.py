"""Feedback endpoint — accepts analyst score adjustments and stores them."""

from fastapi import APIRouter

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/")
async def submit_feedback(user_id: str, score_adjustment: float, comment: str = ""):
    """Record analyst feedback for a user's risk score."""
    raise NotImplementedError("Week 8 — implement feedback endpoint.")
