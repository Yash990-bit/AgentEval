from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field
import enum

class ScenarioTypeEnum(str, enum.Enum):
    business_operations = "business_operations"
    customer_support = "customer_support"
    research_team = "research_team"
    trading_desk = "trading_desk"
    security_ops = "security_ops"
    custom = "custom"

class ScenarioBase(BaseModel):
    name: str
    description: Optional[str] = None
    scenario_type: ScenarioTypeEnum
    agent_configs: List[Any] = Field(default_factory=list)
    environment_config: dict = Field(default_factory=dict)
    success_criteria: dict = Field(default_factory=dict)
    tags: Optional[List[str]] = None
    is_template: bool = False
    is_public: bool = False

class ScenarioCreate(ScenarioBase):
    created_by: UUID

class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    scenario_type: Optional[ScenarioTypeEnum] = None
    agent_configs: Optional[List[Any]] = None
    environment_config: Optional[dict] = None
    success_criteria: Optional[dict] = None
    tags: Optional[List[str]] = None
    is_template: Optional[bool] = None
    is_public: Optional[bool] = None

class ScenarioRead(ScenarioBase):
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
