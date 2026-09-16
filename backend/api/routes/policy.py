"""Policy Violations Route Endpoint (`GET /policy-violations`)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.db import get_db
from api.models import PolicyViolationModel
from api.schemas.policy import PolicyViolationResponse

router = APIRouter()


@router.get(
    "/policy-violations",
    response_model=List[PolicyViolationResponse],
    summary="Get recent triggered automated policy violations",
)
def get_recent_policy_violations(
    limit: int = Query(50, ge=1, le=200, description="Max violation records to return"),
    severity: Optional[str] = Query(
        None, description="Optional severity filter (CRITICAL, HIGH, MEDIUM, LOW)"
    ),
    db: Session = Depends(get_db),
) -> List[PolicyViolationResponse]:
    """Retrieves chronological audit log of triggered automated containment policy violations."""
    query = db.query(PolicyViolationModel).order_by(
        PolicyViolationModel.timestamp.desc()
    )

    if severity:
        query = query.filter(PolicyViolationModel.severity == severity.upper())

    violations = query.limit(limit).all()

    return [
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
