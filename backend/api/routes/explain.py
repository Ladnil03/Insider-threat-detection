"""Explain endpoint — returns SHAP feature attributions for a risk score."""

from fastapi import APIRouter

router = APIRouter(prefix="/explain", tags=["explainability"])


@router.post("/")
async def explain_score(user_id: str, activity_id: str):
    """Return SHAP values for a given activity's risk score."""
    raise NotImplementedError("Week 8 — implement explain endpoint.")
