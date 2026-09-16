"""Policy Violation ORM Model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db import Base


class PolicyViolationModel(Base):
    """Triggered automated security policy violation log entry."""

    __tablename__ = "policy_violations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(
        Integer, ForeignKey("activities.id"), nullable=True, index=True
    )
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    rule_id = Column(String, nullable=False, index=True)
    rule_name = Column(String, nullable=False)
    severity = Column(String, nullable=False, default="HIGH")
    action = Column(String, nullable=False)
    description = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("UserModel", back_populates="policy_violations")
    activity = relationship("ActivityModel", back_populates="policy_violations")
