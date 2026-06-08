from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.models import Base

class AgentPerformanceMetrics(Base):
    __tablename__ = "agent_performance_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    simulation_id = Column(UUID(as_uuid=True), nullable=False)

    goals_completed = Column(Integer, default=0)
    goals_failed = Column(Integer, default=0)
    goals_abandoned = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    efficiency_score = Column(Float, default=0.0)
    cooperation_score = Column(Float, default=0.0)
    reliability_score = Column(Float, default=0.0)
    intelligence_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    composite_score = Column(Float, default=0.0)
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    resource_utilization_pct = Column(Float, default=0.0)
    avg_trust_given = Column(Float, default=0.0)
    avg_trust_received = Column(Float, default=0.0)
    failure_count = Column(Integer, default=0)
    conflict_involvement_count = Column(Integer, default=0)
    overall_rank = Column(Integer, default=0)

    # Optional relationship back‑refs (if needed)
    # simulation = relationship("SimulationAnalytics", back_populates="agent_metrics")

    def __repr__(self) -> str:
        return f"<AgentPerformanceMetrics(agent_id={self.agent_id}, simulation_id={self.simulation_id})>"
