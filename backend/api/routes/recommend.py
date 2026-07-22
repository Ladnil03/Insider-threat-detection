"""Recommend endpoint — returns LLM-generated analyst recommendation."""

from fastapi import APIRouter

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.post("/")
async def get_recommendation(user_id: str, activity_id: str):
    """Generate plain-English recommendation from score + SHAP + context."""
    raise NotImplementedError("Week 8 — implement recommend endpoint.")
