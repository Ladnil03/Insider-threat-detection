"""SQLAlchemy ORM model for risk scores."""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from backend.api.db import Base


class Score(Base):
    """Computed risk score (PRISM, AIRS, blended) for a user activity."""

    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        String(50), ForeignKey("users.user_id"), nullable=False, index=True
    )
    activity_id = Column(Integer, ForeignKey("activities.id"))
    prism_score = Column(Float, default=0.0)
    airs_score = Column(Float, default=0.0)
    blended_score = Column(Float, default=0.0)
    severity_bucket = Column(String(20))
    computed_at = Column(DateTime, server_default=func.now())
