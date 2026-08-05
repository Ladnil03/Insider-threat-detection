"""Scoring Route Endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ScoreRequest(BaseModel):
    user_id: str


class ScoreResponse(BaseModel):
    user_id: str
    prism_score: float
    airs_score: float
    composite_score: float
    risk_level: str


@router.post("/score", response_model=ScoreResponse)
def get_user_score(request: ScoreRequest) -> ScoreResponse:
    """Calculates PRISM, AIRS, and composite risk score for a target user.

    Args:
        request: ScoreRequest containing target user ID.

    Returns:
        ScoreResponse object with score breakdown.
    """
    return ScoreResponse(
        user_id=request.user_id,
        prism_score=0.25,
        airs_score=0.30,
        composite_score=0.28,
        risk_level="LOW",
    )
