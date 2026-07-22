"""SQLAlchemy ORM model for users."""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from backend.api.db import Base


class User(Base):
    """A monitored employee or contractor."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    role = Column(String(50))
    department = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
