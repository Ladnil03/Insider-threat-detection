"""User ORM Model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship

from api.db import Base


class UserModel(Base):
    """User database model representing monitored corporate employees."""

    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="Standard Employee")
    department = Column(String, nullable=False, default="General")
    created_at = Column(DateTime, default=datetime.utcnow)

    activities = relationship(
        "ActivityModel", back_populates="user", cascade="all, delete-orphan"
    )
    scores = relationship(
        "RiskScoreModel", back_populates="user", cascade="all, delete-orphan"
    )
    feedbacks = relationship(
        "FeedbackModel", back_populates="user", cascade="all, delete-orphan"
    )
    policy_violations = relationship(
        "PolicyViolationModel", back_populates="user", cascade="all, delete-orphan"
    )
