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
from sqlalchemy.dialects.postgresql import UUID
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
    tools = Column(JSON, nullable=False, default=list)  # list of tool IDs
    resource_budget = Column(JSON, nullable=False, default=lambda: {
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

class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    state = Column(JSON, nullable=False)  # snapshot of agents, links, etc.

class ResourceLog(Base):
    __tablename__ = "resource_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    tick = Column(Integer, nullable=False)
    resource_budget = Column(JSON)
    energy_score = Column(Float)
    trust_score = Column(Float)
    risk_score = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

# Separate top-level models for resource budgeting and events
class ResourceBudget(Base):
    __tablename__ = "resource_budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    simulation_id = Column(UUID(as_uuid=True), nullable=False)
    compute_total = Column(Integer, default=0)
    compute_used = Column(Integer, default=0)
    compute_reserved = Column(Integer, default=0)
    api_calls_total = Column(Integer, default=0)
    api_calls_used = Column(Integer, default=0)
    tokens_total = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    usd_total = Column(Float, default=0.0)
    usd_spent = Column(Float, default=0.0)
    efficiency_score = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ResourceEvent(Base):
    __tablename__ = "resource_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    simulation_id = Column(UUID(as_uuid=True), nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    resource_type = Column(String, nullable=False)
    action_type = Column(String, nullable=False)  # consumed/reserved/released/transferred
    amount = Column(Integer, nullable=False)
    tick = Column(Integer, nullable=False)
    extra_metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

# Register episodic and shared memory models on Base
from app.models.shared_memory import SharedMemory
from app.models.episodic_memory import EpisodicMemory
