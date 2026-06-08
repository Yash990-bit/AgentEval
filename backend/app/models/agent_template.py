import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Float, JSON, ARRAY, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

import enum

Base = declarative_base()

class RoleEnum(str, enum.Enum):
    RESEARCH = "research"
    CODING = "coding"
    DATA_ANALYST = "data_analyst"
    CUSTOMER_SUPPORT = "customer_support"
    STRATEGIC_PLANNER = "strategic_planner"
    SECURITY_AUDITOR = "security_auditor"
    NEGOTIATOR = "negotiator"
    COORDINATOR = "coordinator"
    CUSTOM = "custom"

class AgentTemplate(Base):
    __tablename__ = "agent_templates"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by = Column(PG_UUID(as_uuid=True), nullable=False)
    name = Column(String(80), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    description = Column(String(500), nullable=True)
    system_prompt = Column(String(2000), nullable=False)
    default_objective_template = Column(String, nullable=True)
    default_tools = Column(ARRAY(String), nullable=True)
    default_resource_budget = Column(JSON, nullable=True)
    default_trust_score = Column(Float, nullable=True)
    personality_traits = Column(JSON, nullable=True)  # expects dict with bias, tolerance, verbosity
    tags = Column(ARRAY(String), nullable=True)
    version = Column(String, nullable=False, default="1.0.0")
    is_public = Column(Boolean, default=False)
    use_count = Column(Integer, default=0)
    avg_performance_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
