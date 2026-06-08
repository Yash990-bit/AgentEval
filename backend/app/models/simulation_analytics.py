from sqlalchemy import Column, Integer, Float, String, Enum, JSON, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.db.models import Base

class CompletionStatus(str, enum.Enum):
    success = "success"
    partial_success = "partial_success"
    failure = "failure"
    timeout = "timeout"

class SimulationAnalytics(Base):
    __tablename__ = "simulation_analytics"

    simulation_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    total_ticks_run = Column(Integer, nullable=False)
    total_agents = Column(Integer, nullable=False)
    total_goals = Column(Integer, nullable=False)
    overall_success_rate = Column(Float, nullable=False)
    overall_failure_rate = Column(Float, nullable=False)
    avg_efficiency_score = Column(Float, nullable=False)
    avg_trust_score = Column(Float, nullable=False)
    avg_intelligence_score = Column(Float, default=0.0)
    avg_cooperation_score = Column(Float, default=0.0)
    avg_reliability_score = Column(Float, default=0.0)
    avg_risk_score = Column(Float, default=0.0)
    total_conflicts_detected = Column(Integer, nullable=False)
    conflicts_auto_resolved = Column(Integer, nullable=False)
    conflicts_escalated = Column(Integer, nullable=False)
    total_emergent_behaviors = Column(Integer, nullable=False)
    total_resource_units_consumed = Column(JSON, nullable=False)
    total_waste_rate = Column(Float, nullable=False)
    top_performing_agent_id = Column(UUID(as_uuid=True), nullable=True)
    most_conflicted_agent_id = Column(UUID(as_uuid=True), nullable=True)
    completion_status = Column(Enum(CompletionStatus), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
