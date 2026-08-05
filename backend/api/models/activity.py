"""Activity Log ORM Model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String

from api.db import Base


class ActivityModel(Base):
    """Daily aggregated user activity feature log record."""

    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    logon_after_hours = Column(Float, default=0.0)
    usb_file_copy = Column(Float, default=0.0)
    email_external_count = Column(Float, default=0.0)
    web_job_search_count = Column(Float, default=0.0)
