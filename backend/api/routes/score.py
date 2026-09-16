"""Scoring Route Endpoint (`POST /score`)."""

import json
import logging
from datetime import datetime
from typing import Any, Dict

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from airs.ensemble import compute_ensemble_score
from airs.inference import score_activity_features
from api.db import get_db
from api.models import ActivityModel, PolicyViolationModel, RiskScoreModel, UserModel
from api.schemas.score import PolicyActionSummary, ScoreRequest, ScoreResponse
from data_pipeline.config import ALL_FEATURE_COLS
from policy_engine.engine import evaluate_policy_rules
from prism.buckets import classify_risk_score
from prism.scorer import score_activity_row

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/score",
    response_model=ScoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Compute multi-model risk scores on submitted user activity",
)
def compute_and_record_score(
    request: ScoreRequest,
    db: Session = Depends(get_db),
) -> ScoreResponse:
    """Computes PRISM rule-based score, AIRS autoencoder anomaly score, and Ensemble score

    for an activity event, evaluates automated security policies, records all artifacts to the database,
    and returns a complete structured score response.
    """
    user_id = request.user_id.strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id cannot be empty",
        )

    # 1. Ensure user exists or create placeholder
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        user = UserModel(
            user_id=user_id,
            user_name=user_id,
            role=request.user_role or "Standard Employee",
            department="General",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    metrics = request.metrics or {}

    # 2. Compute PRISM rule score
    try:
        prism_score = float(score_activity_row(metrics))
    except Exception as e:
        logger.warning(f"Error computing PRISM score: {e}. Defaulting to 0.25")
        prism_score = 0.25

    # 3. Compute AIRS autoencoder reconstruction score
    try:
        # Build 72-feature aligned array
        feat_arr = np.array(
            [float(metrics.get(col, 0.0)) for col in ALL_FEATURE_COLS],
            dtype=np.float32,
        )
        airs_res = score_activity_features(feat_arr)
        airs_score = float(airs_res.get("sai_score", 0.0))
    except Exception as e:
        logger.warning(f"Error computing AIRS score: {e}. Defaulting to 0.20")
        airs_score = 0.20

    # 4. Compute Ensemble score
    ensemble_score = float(compute_ensemble_score(prism_score, airs_score))
    risk_level = classify_risk_score(ensemble_score)

    # 5. Save Activity in DB
    date_day = request.date_day or datetime.utcnow().strftime("%Y-%m-%d")
    activity = ActivityModel(
        user_id=user_id,
        date_day=date_day,
        metrics_json=json.dumps(metrics),
        created_at=datetime.utcnow(),
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    # 6. Save Score Record in DB
    score_record = RiskScoreModel(
        activity_id=activity.id,
        user_id=user_id,
        prism_score=round(prism_score, 4),
        airs_score=round(airs_score, 4),
        ensemble_score=round(ensemble_score, 4),
        risk_level=risk_level,
        timestamp=activity.created_at,
    )
    db.add(score_record)

    # 7. Evaluate Policy Rules & Record Triggered Violations
    eval_metrics: Dict[str, Any] = dict(metrics)
    eval_metrics["risk_score"] = ensemble_score
    eval_metrics["sai_score"] = airs_score
    eval_metrics["prism_score"] = prism_score

    triggered_rules = evaluate_policy_rules(eval_metrics)
    policy_summaries = []

    for rule_event in triggered_rules:
        violation = PolicyViolationModel(
            activity_id=activity.id,
            user_id=user_id,
            rule_id=rule_event["rule_id"],
            rule_name=rule_event["rule_name"],
            severity=rule_event.get("severity", "HIGH"),
            action=rule_event["action"],
            description=rule_event.get("description", ""),
            timestamp=activity.created_at,
        )
        db.add(violation)
        policy_summaries.append(
            PolicyActionSummary(
                rule_id=rule_event["rule_id"],
                rule_name=rule_event["rule_name"],
                severity=rule_event.get("severity", "HIGH"),
                action=rule_event["action"],
                description=rule_event.get("description"),
            )
        )

    db.commit()

    return ScoreResponse(
        activity_id=activity.id,
        user_id=user_id,
        prism_score=round(prism_score, 4),
        airs_score=round(airs_score, 4),
        ensemble_score=round(ensemble_score, 4),
        risk_level=risk_level,
        timestamp=activity.created_at,
        triggered_policies=policy_summaries,
    )
