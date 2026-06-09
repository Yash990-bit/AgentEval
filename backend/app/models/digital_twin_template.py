from sqlalchemy import Column, Integer, String, Boolean, JSON, Enum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid
from app.db.models import Base

class TwinType(str, enum.Enum):
    support_team = "support_team"
    dev_team = "dev_team"
    sales_team = "sales_team"
    ops_team = "ops_team"
    research_lab = "research_lab"
    trading_desk = "trading_desk"
    security_team = "security_team"
    custom = "custom"

class DigitalTwinTemplate(Base):
    __tablename__ = "digital_twin_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    industry = Column(String, nullable=False)
    twin_type = Column(Enum(TwinType), nullable=False)
    org_structure = Column(JSON, nullable=False)  # hierarchical role definitions
    default_agent_count = Column(Integer, nullable=False)
    default_scenario_config = Column(JSON, nullable=False)
    real_world_kpis = Column(JSON, nullable=False)
    is_public = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
