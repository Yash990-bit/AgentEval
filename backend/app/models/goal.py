from __future__ import annotations

import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class GoalStatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    blocked = "blocked"
    completed = "completed"
    abandoned = "abandoned"
    failed = "failed"

class AgentGoal(Base):
    __tablename__ = "agent_goals"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), nullable=False)
    simulation_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    priority = Column(Integer, default=5)
    parent_goal_id = Column(UUID(as_uuid=True), ForeignKey("agent_goals.id"), nullable=True)
    dependencies = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    deadline_tick = Column(Integer, nullable=True)
    required_resources = Column(JSON, nullable=True)  # {compute_units, api_calls, tokens}
    status = Column(Enum(GoalStatusEnum), default=GoalStatusEnum.pending, nullable=False)
    progress_pct = Column(Float, default=0.0)
    started_tick = Column(Integer, nullable=True)
    completed_tick = Column(Integer, nullable=True)
    abandoned_tick = Column(Integer, nullable=True)
    completion_notes = Column(String, nullable=True)
    abandonment_reason = Column(String, nullable=True)
    # Relationships
    parent = relationship('AgentGoal', remote_side=[id], backref='subgoals', uselist=False)
