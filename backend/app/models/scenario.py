import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ScenarioTypeEnum(str, Enum):
    business_operations = "business_operations"
    customer_support = "customer_support"
    research_team = "research_team"
    trading_desk = "trading_desk"
    security_ops = "security_ops"
    custom = "custom"

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by = Column(PG_UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    scenario_type = Column(Enum(ScenarioTypeEnum), nullable=False)
    agent_configs = Column(JSON, nullable=False)  # list of AgentConfig objects
    environment_config = Column(JSON, nullable=True)
    success_criteria = Column(JSON, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    is_template = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
