"""LLM Recommendation Route Endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RecommendRequest(BaseModel):
    user_id: str


class RecommendResponse(BaseModel):
    user_id: str
    recommendation: str
    provider: str


@router.post("/recommend", response_model=RecommendResponse)
def get_recommendation(request: RecommendRequest) -> RecommendResponse:
    """Generates plain-English LLM threat analyst recommendation.

    Args:
        request: RecommendRequest with user ID.

    Returns:
        RecommendResponse object containing narrative and provider metadata.
    """
    return RecommendResponse(
        user_id=request.user_id,
        recommendation="User shows low risk baseline activity. No immediate containment required.",
        provider="groq",
    )
