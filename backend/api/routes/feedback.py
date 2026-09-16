"""Analyst Feedback Route Endpoint (`POST /feedback`)."""

import json
import logging
from datetime import datetime

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from airs.feedback import FeedbackBuffer, blend_analyst_feedback
from api.db import get_db
from api.models import ActivityModel, FeedbackModel, RiskScoreModel
from api.schemas.feedback import FeedbackCreateRequest, FeedbackResponse
from data_pipeline.config import ALL_FEATURE_COLS

logger = logging.getLogger(__name__)
router = APIRouter()

# Global feedback buffer singleton tracking feedback count for retraining
_global_feedback_buffer = FeedbackBuffer(retrain_threshold=50)


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit analyst risk score adjustment and blend feedback",
)
def submit_analyst_feedback(
    request: FeedbackCreateRequest,
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    """Accepts manual risk adjustment from SOC analyst, computes blended adaptive score

    (S_final = (1-alpha)*S_AI + alpha*S_user), persists feedback entry to database,
    and signals if retraining threshold (N=50) is reached.
    """
    activity = (
        db.query(ActivityModel).filter(ActivityModel.id == request.activity_id).first()
    )
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {request.activity_id} not found",
        )

    score_record = (
        db.query(RiskScoreModel)
        .filter(RiskScoreModel.activity_id == request.activity_id)
        .order_by(RiskScoreModel.id.desc())
        .first()
    )

    original_score = score_record.ensemble_score if score_record else 0.50

    # Mathematical feedback blending: S_final = (1 - alpha)*S_orig + alpha*S_adj
    blended_score = float(
        blend_analyst_feedback(
            model_score=original_score,
            analyst_score=request.adjusted_score,
            alpha=0.7,
        )
    )

    # Save to database
    feedback_entry = FeedbackModel(
        activity_id=request.activity_id,
        user_id=request.user_id,
        original_score=round(original_score, 4),
        adjusted_score=round(request.adjusted_score, 4),
        blended_score=round(blended_score, 4),
        notes=request.notes,
        timestamp=datetime.utcnow(),
    )
    db.add(feedback_entry)
    db.commit()
    db.refresh(feedback_entry)

    # Parse feature vector if available for buffer
    try:
        metrics = json.loads(activity.metrics_json) if activity.metrics_json else {}
        feat_vec = np.array(
            [float(metrics.get(c, 0.0)) for c in ALL_FEATURE_COLS],
            dtype=np.float32,
        )
    except Exception:
        feat_vec = np.zeros(len(ALL_FEATURE_COLS), dtype=np.float32)

    # Append to in-memory retraining buffer
    _global_feedback_buffer.add_feedback(
        activity_id=str(request.activity_id),
        sai_score=original_score,
        user_score=request.adjusted_score,
        feature_vector=feat_vec,
        alpha=0.7,
    )
    retrain_triggered = _global_feedback_buffer.is_ready_for_retraining()

    if retrain_triggered:
        logger.info(
            "Retraining threshold reached in FeedbackBuffer! Autoencoder incremental update ready."
        )

    return FeedbackResponse(
        feedback_id=feedback_entry.id,
        activity_id=feedback_entry.activity_id,
        user_id=feedback_entry.user_id,
        original_score=feedback_entry.original_score,
        adjusted_score=feedback_entry.adjusted_score,
        blended_score=feedback_entry.blended_score,
        notes=feedback_entry.notes,
        retrain_threshold_reached=retrain_triggered,
        timestamp=feedback_entry.timestamp,
    )
