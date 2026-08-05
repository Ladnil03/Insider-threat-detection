"""User ORM Model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, String

from api.db import Base


class UserModel(Base):
    """User database model representing monitored corporate employees."""

    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    department = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
