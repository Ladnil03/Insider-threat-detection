"""Analyst Feedback ORM Model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from api.db import Base


class FeedbackModel(Base):
    """Analyst manual risk adjustment and feedback entry."""

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    original_score = Column(Float, nullable=False)
    adjusted_score = Column(Float, nullable=False)
    notes = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
