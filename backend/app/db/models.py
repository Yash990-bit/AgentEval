# backend/app/db/models.py
"""SQLAlchemy models for the simulation backend.

This schema follows the specification for the AABS project.
"""

import enum
import uuid
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    JSON,
    DateTime,
    Enum as SAEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AgentRole(enum.Enum):
    researcher = "researcher"
    planner = "planner"
    executor = "executor"
    analyst = "analyst"
    coordinator = "coordinator"
    support = "support"
    custom = "custom"

class AgentStatus(enum.Enum):
    idle = "idle"
    running = "running"
    sleeping = "sleeping"
    failed = "failed"
    completed = "completed"

class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    role = Column(SAEnum(AgentRole), nullable=False)
    objective = Column(String(500), nullable=False)
    tools = Column(JSONB, nullable=False, default=list)  # list of tool IDs
    resource_budget = Column(JSONB, nullable=False, default=lambda: {
        "compute_units": 0,
        "api_calls": 0,
        "tokens": 0,
        "usd_budget": 0.0,
    })
    trust_score = Column(Float, nullable=False, default=0.5)
    energy_score = Column(Float, nullable=False, default=1.0)
    risk_score = Column(Float, nullable=False, default=0.0)
    status = Column(SAEnum(AgentStatus), nullable=False, default=AgentStatus.idle)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    state = Column(JSONB, nullable=False)  # snapshot of agents, links, etc.

class ResourceLog(Base):
    __tablename__ = "resource_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    tick = Column(Integer, nullable=False)
    resource_budget = Column(JSONB)
    energy_score = Column(Float)
    trust_score = Column(Float)
    risk_score = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
