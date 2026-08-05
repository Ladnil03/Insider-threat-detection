"""Risk Score ORM Model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from api.db import Base


class RiskScoreModel(Base):
    """Historical risk score computation record."""

    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    prism_score = Column(Float, nullable=False)
    airs_score = Column(Float, nullable=False)
    composite_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
