"""User History and Directory Endpoints (`GET /users/{user_id}/history`, `GET /users`)."""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import ActivityModel, PolicyViolationModel, RiskScoreModel, UserModel
from api.schemas.policy import PolicyViolationResponse
from api.schemas.user import (
    UserActivityHistoryItem,
    UserHistoryResponse,
    UserSummaryResponse,
)

router = APIRouter()


@router.get(
    "/users",
    response_model=List[UserSummaryResponse],
    summary="List all monitored users with their latest risk status",
)
def get_monitored_users(
    db: Session = Depends(get_db),
) -> List[UserSummaryResponse]:
    """Returns directory of all monitored users, latest computed risk scores, and violation counts."""
    users = db.query(UserModel).all()
    summaries = []

    for u in users:
        latest_score = (
            db.query(RiskScoreModel)
            .filter(RiskScoreModel.user_id == u.user_id)
            .order_by(RiskScoreModel.timestamp.desc())
            .first()
        )
        latest_activity = (
            db.query(ActivityModel)
            .filter(ActivityModel.user_id == u.user_id)
            .order_by(ActivityModel.created_at.desc())
            .first()
        )
        violation_count = (
            db.query(PolicyViolationModel)
            .filter(PolicyViolationModel.user_id == u.user_id)
            .count()
        )

        summaries.append(
            UserSummaryResponse(
                user_id=u.user_id,
                user_name=u.user_name,
                role=u.role,
                department=u.department,
                latest_score=latest_score.ensemble_score if latest_score else 0.0,
                risk_level=latest_score.risk_level if latest_score else "LOW",
                latest_activity_date=(
                    latest_activity.date_day if latest_activity else None
                ),
                violation_count=violation_count,
            )
        )

    return summaries


@router.get(
    "/users/{user_id}/history",
    response_model=UserHistoryResponse,
    summary="Get complete timeline and score history for a user",
)
def get_user_history(
    user_id: str,
    db: Session = Depends(get_db),
) -> UserHistoryResponse:
    """Retrieves full longitudinal history of daily activities, risk score progressions,

    and triggered policy alerts for a target user.
    """
    user = db.query(UserModel).filter(UserModel.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        )

    activities = (
        db.query(ActivityModel)
        .filter(ActivityModel.user_id == user_id)
        .order_by(ActivityModel.created_at.asc())
        .all()
    )

    history_items = []
    latest_score = 0.0
    latest_level = "LOW"

    for act in activities:
        score_rec = (
            db.query(RiskScoreModel)
            .filter(RiskScoreModel.activity_id == act.id)
            .first()
        )
        try:
            metrics = json.loads(act.metrics_json) if act.metrics_json else {}
        except Exception:
            metrics = {}

        p_score = score_rec.prism_score if score_rec else 0.0
        a_score = score_rec.airs_score if score_rec else 0.0
        e_score = score_rec.ensemble_score if score_rec else 0.0
        r_level = score_rec.risk_level if score_rec else "LOW"

        latest_score = e_score
        latest_level = r_level

        history_items.append(
            UserActivityHistoryItem(
                activity_id=act.id,
                date_day=act.date_day,
                timestamp=act.created_at,
                prism_score=p_score,
                airs_score=a_score,
                ensemble_score=e_score,
                risk_level=r_level,
                metrics=metrics,
            )
        )

    violations = (
        db.query(PolicyViolationModel)
        .filter(PolicyViolationModel.user_id == user_id)
        .order_by(PolicyViolationModel.timestamp.desc())
        .all()
    )

    policy_responses = [
        PolicyViolationResponse(
            id=v.id,
            activity_id=v.activity_id,
            user_id=v.user_id,
            rule_id=v.rule_id,
            rule_name=v.rule_name,
            severity=v.severity,
            action=v.action,
            description=v.description,
            timestamp=v.timestamp,
        )
        for v in violations
    ]

    return UserHistoryResponse(
        user_id=user.user_id,
        user_name=user.user_name,
        role=user.role,
        department=user.department,
        current_risk_score=latest_score,
        current_risk_level=latest_level,
        history=history_items,
        policy_violations=policy_responses,
    )
