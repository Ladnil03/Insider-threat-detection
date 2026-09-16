"""Risk Score ORM Model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db import Base


class RiskScoreModel(Base):
    """Historical risk score computation record."""

    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(
        Integer, ForeignKey("activities.id"), nullable=False, index=True
    )
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    prism_score = Column(Float, nullable=False, default=0.0)
    airs_score = Column(Float, nullable=False, default=0.0)
    ensemble_score = Column(Float, nullable=False, default=0.0)
    risk_level = Column(String, nullable=False, default="LOW")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("UserModel", back_populates="scores")
    activity = relationship("ActivityModel", back_populates="scores")
