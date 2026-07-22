"""SQLAlchemy ORM model for analyst feedback."""

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.sql import func

from backend.api.db import Base


class Feedback(Base):
    """Analyst score adjustment recorded for a user."""

    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        String(50), ForeignKey("users.user_id"), nullable=False, index=True
    )
    score_adjustment = Column(Float, default=0.0)
    comment = Column(String(1000))
    created_at = Column(DateTime, server_default=func.now())
