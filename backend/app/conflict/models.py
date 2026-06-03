# backend/app/conflict/models.py
"""SQLAlchemy models for conflict detection."""

import uuid
from enum import Enum

from sqlalchemy import Column, String, Float, Integer, Enum as SAEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.models import Base

class ConflictType(str, Enum):
    GOAL = "Goal Conflict"
    RESOURCE = "Resource Conflict"
    COMMUNICATION = "Communication Conflict"
    TRUST = "Trust Breakdown"
    DEADLOCK = "Deadlock"
    PRIORITY_INVERSION = "Priority Inversion"

class ConflictStatus(str, Enum):
    ACTIVE = "active"
    AUTO_RESOLVED = "auto_resolved"
    MANUALLY_RESOLVED = "manually_resolved"
    ESCALATED = "escalated"
    IGNORED = "ignored"

class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), nullable=False)
    conflict_type = Column(SAEnum(ConflictType, native_enum=False), nullable=False)
    detected_at_tick = Column(Integer, nullable=False)
    # Use JSON column to store the list of agent ID strings, ensuring SQLite and Postgres compatibility
    agents_involved = Column(JSON, nullable=False)
    severity_score = Column(Float, nullable=False)
    root_cause = Column(String(200), nullable=False)
    suggested_resolution = Column(String, nullable=False)
    status = Column(SAEnum(ConflictStatus, native_enum=False), nullable=False, default=ConflictStatus.ACTIVE)
    resolved_at_tick = Column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<Conflict {self.id} type={self.conflict_type} severity={self.severity_score:.2f}>"
