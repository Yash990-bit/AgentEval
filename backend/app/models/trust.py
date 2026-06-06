from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.models import Base

class AgentTrustEdge(Base):
    __tablename__ = "agent_trust_edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    simulation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    source_agent_id = Column(String, nullable=False, index=True)
    target_agent_id = Column(String, nullable=False, index=True)
    trust_score = Column(Float, nullable=False, default=0.0)
    influence_score = Column(Float, nullable=False, default=0.0)
    last_updated_tick = Column(Integer, nullable=False, default=0)
    # JSON array of objects {"tick": int, "score": float}
    history = Column(JSON, nullable=False, default=list)

    __table_args__ = (
        # Composite index for quick lookups
        # (simulation_id, source_agent_id, target_agent_id)
        # Note: SQLAlchemy syntax for index can be added via Index if needed
        {}
    )

    def record_history(self, tick: int, score: float):
        if not isinstance(self.history, list):
            self.history = []
        self.history.append({"tick": tick, "score": score})
