"""Explainability Route Endpoint (`GET /explain/{activity_id}`)."""

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import ActivityModel
from api.schemas.explain import ExplainResponse, FeatureAttribution
from explainability.shap_explainer import AIRSShapExplainer
from explainability.visualize import format_shap_summary_dict

logger = logging.getLogger(__name__)
router = APIRouter()

# Persistent global singleton explainer instance
_global_explainer: Optional[AIRSShapExplainer] = None


def get_shared_explainer() -> AIRSShapExplainer:
    """Returns singleton explainer instance to leverage cached background model."""
    global _global_explainer
    if _global_explainer is None:
        try:
            _global_explainer = AIRSShapExplainer(background_samples=25)
        except Exception as e:
            logger.warning(
                f"Could not load checkpoint for explainer: {e}. Initializing synthetic baseline."
            )
            _global_explainer = AIRSShapExplainer(background_samples=10)
    return _global_explainer


@router.get(
    "/explain/{activity_id}",
    response_model=ExplainResponse,
    summary="Get SHAP feature attribution breakdown for an activity",
)
def get_activity_explanation(
    activity_id: int,
    top_k: int = Query(
        5, ge=1, le=20, description="Number of top risk drivers to highlight"
    ),
    db: Session = Depends(get_db),
) -> ExplainResponse:
    """Generates local SHAP feature attributions and risk contribution percentages

    for a specified recorded activity.
    """
    activity = db.query(ActivityModel).filter(ActivityModel.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {activity_id} not found",
        )

    try:
        metrics = json.loads(activity.metrics_json) if activity.metrics_json else {}
    except Exception:
        metrics = {}

    explainer = get_shared_explainer()
    cache_key = f"activity_{activity_id}_topk_{top_k}"

    try:
        raw_exp = explainer.explain_activity(
            activity_record=metrics,
            top_k=top_k,
            nsamples=100,
            use_cache=True,
            custom_cache_key=cache_key,
        )
        formatted = format_shap_summary_dict(raw_exp)
    except Exception as e:
        logger.error(f"Error computing SHAP attribution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SHAP explanation: {str(e)}",
        )

    features = [
        FeatureAttribution(
            feature=f["feature"],
            raw_key=f["raw_key"],
            attribution=float(f["attribution"]),
            value=float(f["value"]),
            percentage=float(f["percentage"]),
            direction=f["direction"],
        )
        for f in formatted.get("features", [])
    ]

    return ExplainResponse(
        activity_id=activity_id,
        user_id=activity.user_id,
        base_value=float(formatted.get("base_value", 0.0)),
        reconstruction_error=float(formatted.get("reconstruction_error", 0.0)),
        sai_score=float(formatted.get("sai_score", 0.0)),
        human_readable_summary=formatted.get("human_readable_summary", ""),
        top_risk_drivers=formatted.get("top_risk_drivers", []),
        features=features,
    )
