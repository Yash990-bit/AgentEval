# backend/app/models/episodic_memory.py
"""SQLAlchemy model for episodic memory records."""

from sqlalchemy import Column, Integer, String, JSON, Float, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.models import Base

class EpisodicMemory(Base):
    __tablename__ = "episodic_memories"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, index=True)
    simulation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tick = Column(Integer, nullable=False)
    episode_type = Column(String, nullable=False)
    context_snapshot = Column(JSON, nullable=False)
    outcome = Column(String, nullable=True)
    emotional_valence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
