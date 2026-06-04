# backend/app/resource/models.py
"""SQLAlchemy models for the Resource Management System.

Defines:
* ResourceBudget – per‑agent budget tracking.
* ResourceEvent – log of consumption/reservation/release/waste actions.
"""

from datetime import datetime
import enum
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from app.db.models import Base

class ResourceType(str, enum.Enum):
    COMPUTE_UNITS = "compute_units"
    API_CALLS = "api_calls"
    MEMORY_SLOTS = "memory_slots"
    TOKEN_BUDGET = "token_budget"
    USD_BUDGET = "usd_budget"

class ActionType(str, enum.Enum):
    CONSUMED = "consumed"
    RESERVED = "reserved"
    RELEASED = "released"
    TRANSFERRED = "transferred"
    WASTED = "wasted"

class ResourceBudget(Base):
    __tablename__ = "resource_budgets"
    __table_args__ = {'extend_existing': True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String, nullable=False)
    simulation_id = Column(UUID(as_uuid=True), nullable=False)

    # Totals
    compute_total = Column(Integer, default=0)
    api_calls_total = Column(Integer, default=0)
    memory_slots_total = Column(Integer, default=0)
    tokens_total = Column(Integer, default=0)
    usd_total = Column(Float, default=0.0)

    # Used / reserved
    compute_used = Column(Integer, default=0)
    api_calls_used = Column(Integer, default=0)
    memory_slots_used = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    usd_spent = Column(Float, default=0.0)

    compute_reserved = Column(Integer, default=0)
    api_calls_reserved = Column(Integer, default=0)
    memory_slots_reserved = Column(Integer, default=0)
    tokens_reserved = Column(Integer, default=0)
    usd_reserved = Column(Float, default=0.0)

    efficiency_score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ResourceEvent(Base):
    __tablename__ = "resource_events"
    __table_args__ = {'extend_existing': True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), nullable=False)
    agent_id = Column(String, nullable=False)
    resource_type = Column(SAEnum(ResourceType, native_enum=False), nullable=False)
    action_type = Column(SAEnum(ActionType, native_enum=False), nullable=False)
    amount = Column(Float, nullable=False)
    tick = Column(Integer, nullable=False)
    metadata_ = Column('metadata', JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
