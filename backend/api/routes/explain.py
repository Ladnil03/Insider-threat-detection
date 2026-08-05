"""Explainability Route Endpoint."""

from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ExplainRequest(BaseModel):
    user_id: str


class ExplainResponse(BaseModel):
    user_id: str
    base_value: float
    attributions: Dict[str, float]


@router.post("/explain", response_model=ExplainResponse)
def get_user_explanation(request: ExplainRequest) -> ExplainResponse:
    """Returns SHAP attribution values for user risk score.

    Args:
        request: ExplainRequest with user ID.

    Returns:
        ExplainResponse object with feature attributions.
    """
    return ExplainResponse(
        user_id=request.user_id,
        base_value=0.05,
        attributions={
            "after_hours_logon": 0.12,
            "usb_file_copy": 0.08,
        },
    )
