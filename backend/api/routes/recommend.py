"""Recommendation Route Endpoint (`GET /recommend/{activity_id}`)."""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import ActivityModel, PolicyViolationModel, RiskScoreModel, UserModel
from api.routes.explain import get_shared_explainer
from api.schemas.recommend import RecommendationResponse, RiskDriver
from llm_service.recommend import get_threat_recommendation

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/recommend/{activity_id}",
    response_model=RecommendationResponse,
    summary="Get LLM plain-English threat summary and SOC recommendation",
)
def get_activity_recommendation(
    activity_id: int,
    db: Session = Depends(get_db),
) -> RecommendationResponse:
    """Generates an LLM threat narrative, key risk driver analysis, and actionable SOC

    mitigation recommendations for a specified activity record.
    """
    activity = db.query(ActivityModel).filter(ActivityModel.id == activity_id).first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {activity_id} not found",
        )

    score_record = (
        db.query(RiskScoreModel)
        .filter(RiskScoreModel.activity_id == activity_id)
        .order_by(RiskScoreModel.id.desc())
        .first()
    )
    user = db.query(UserModel).filter(UserModel.user_id == activity.user_id).first()
    violations = (
        db.query(PolicyViolationModel)
        .filter(PolicyViolationModel.activity_id == activity_id)
        .all()
    )

    try:
        metrics = json.loads(activity.metrics_json) if activity.metrics_json else {}
    except Exception:
        metrics = {}

    risk_score = score_record.ensemble_score if score_record else 0.50
    risk_level = score_record.risk_level if score_record else "MODERATE"
    prism_score = score_record.prism_score if score_record else 0.50
    sai_score = score_record.airs_score if score_record else 0.50

    # Retrieve SHAP explanation for the activity
    explainer = get_shared_explainer()
    cache_key = f"activity_{activity_id}_topk_3"
    try:
        shap_res = explainer.explain_activity(
            activity_record=metrics,
            top_k=3,
            nsamples=80,
            use_cache=True,
            custom_cache_key=cache_key,
        )
    except Exception as e:
        logger.warning(f"Failed to generate SHAP in recommendation route: {e}")
        shap_res = {"top_risk_drivers": []}

    policy_events = [
        {
            "rule_id": v.rule_id,
            "rule_name": v.rule_name,
            "severity": v.severity,
            "action": v.action,
        }
        for v in violations
    ]

    rec = get_threat_recommendation(
        user_id=activity.user_id,
        risk_score=risk_score,
        risk_level=risk_level,
        prism_score=prism_score,
        sai_score=sai_score,
        shap_explanation=shap_res,
        recent_activity=metrics,
        user_role=user.role if user else "Standard Employee",
        policy_violations=policy_events,
    )

    risk_drivers = [
        RiskDriver(
            feature=d.get("feature", "Risk Factor"),
            impact=d.get("impact", "HIGH"),
            description=d.get("description", "Elevated activity detected."),
        )
        for d in rec.get("risk_drivers", [])
    ]

    return RecommendationResponse(
        activity_id=activity_id,
        user_id=activity.user_id,
        risk_score=round(risk_score, 4),
        risk_level=risk_level,
        summary=rec.get("summary", "Analysis completed."),
        risk_drivers=risk_drivers,
        recommended_action=rec.get(
            "recommended_action", "Conduct standard supervisor review."
        ),
        urgency=rec.get("urgency", risk_level),
        model=rec.get("model"),
        provider=rec.get("provider"),
        status=rec.get("status", "success"),
    )
