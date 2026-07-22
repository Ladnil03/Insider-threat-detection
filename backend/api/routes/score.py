"""Score endpoint — computes PRISM + AIRS risk score for a user/activity."""

from fastapi import APIRouter

router = APIRouter(prefix="/score", tags=["scoring"])


@router.post("/")
async def compute_score(user_id: str):
    """Compute combined PRISM + AIRS risk score for a user."""
    raise NotImplementedError("Week 8 — implement scoring endpoint.")
