import enum
from sqlalchemy import Column, Float, Integer, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from uuid import uuid4

from app.db.models import Base

class RelationshipType(str, enum.Enum):
    neutral = "neutral"
    allied = "allied"
    rival = "rival"
    blocked = "blocked"

class AgentRelationship(Base):
    __tablename__ = "agent_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    simulation_id = Column(UUID(as_uuid=True), ForeignKey("simulations.id"), nullable=False, index=True)
    agent_a_id = Column(String, nullable=False, index=True)
    agent_b_id = Column(String, nullable=False, index=True)
    relationship_type = Column(Enum(RelationshipType), default=RelationshipType.neutral, nullable=False)
    trust_score = Column(Float, default=0.0)
    interaction_count = Column(Integer, default=0)
    last_interaction_tick = Column(Integer, default=0)
