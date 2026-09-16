"""Activity Log ORM Model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from api.db import Base


class ActivityModel(Base):
    """Daily aggregated user activity feature log record."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    date_day = Column(String, nullable=True, index=True)
    metrics_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("UserModel", back_populates="activities")
    scores = relationship(
        "RiskScoreModel", back_populates="activity", cascade="all, delete-orphan"
    )
    policy_violations = relationship(
        "PolicyViolationModel", back_populates="activity", cascade="all, delete-orphan"
    )
    feedbacks = relationship(
        "FeedbackModel", back_populates="activity", cascade="all, delete-orphan"
    )
