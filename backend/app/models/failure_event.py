# backend/app/models/failure_event.py
"""SQLAlchemy model for failure simulation events."""

from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.models import Base

class FailureEvent(Base):
    __tablename__ = "failure_events"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    failure_type = Column(String, nullable=False)
    tick_occurred = Column(Integer, nullable=False)
    severity = Column(String, nullable=False)  # enum: low, medium, high, critical
    propagated_to = Column(JSON, default=list)  # list of agent IDs (strings)
    recovery_action = Column(String, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at_tick = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
