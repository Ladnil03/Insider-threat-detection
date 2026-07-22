"""SQLAlchemy ORM model for activity records."""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from backend.api.db import Base


class Activity(Base):
    """A single activity event logged for a user."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        String(50), ForeignKey("users.user_id"), nullable=False, index=True
    )
    timestamp = Column(DateTime, nullable=False)
    activity_type = Column(String(100))
    description = Column(String(500))
    risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
