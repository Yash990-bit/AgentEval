# backend/app/db/models.py
"""SQLAlchemy models for the simulation backend.
We keep the schema simple for the demo:
- AgentModel mirrors the fields from the Pydantic Agent schema.
- SimulationRun stores a snapshot of the agents/links JSON for historic queries.
- ResourceLog records per‑tick resource consumption for analytics.
"""

from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AgentModel(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    objective = Column(String, nullable=False)
    # Scores stored as floats for easy arithmetic
    resource_budget = Column(Float, default=100.0)
    trust_score = Column(Float, default=1.0)
    energy_score = Column(Float, default=100.0)
    risk_score = Column(Float, default=0.0)
    status = Column(String, default="idle")

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    # Store the whole state as JSON for quick retrieval
    state = Column(JSON, nullable=False)

class ResourceLog(Base):
    __tablename__ = "resource_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, nullable=False)
    tick = Column(Integer, nullable=False)
    resource_budget = Column(Float)
    energy_score = Column(Float)
    trust_score = Column(Float)
    risk_score = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
