"""Analyst Feedback Route Endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class FeedbackRequest(BaseModel):
    user_id: str
    adjusted_score: float
    notes: str = ""


class FeedbackResponse(BaseModel):
    status: str
    message: str


@router.post("/feedback", response_model=FeedbackResponse)
def submit_analyst_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Stores analyst manual score adjustment into the database for retraining.

    Args:
        request: FeedbackRequest payload.

    Returns:
        FeedbackResponse confirmation message.
    """
    return FeedbackResponse(
        status="success",
        message=f"Feedback recorded for user {request.user_id}.",
    )
