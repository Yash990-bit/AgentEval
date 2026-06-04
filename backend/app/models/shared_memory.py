# backend/app/models/shared_memory.py
"""SQLAlchemy model for the shared memory pool.
Versioned per (simulation_id, agent_id, content)."""

from sqlalchemy import Column, Integer, String, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.models import Base

class SharedMemory(Base):
    __tablename__ = "shared_memory_pools"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    agent_id = Column(String, nullable=False, index=True)
    content = Column(String, nullable=False)
    tags = Column(JSON, default=list)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
