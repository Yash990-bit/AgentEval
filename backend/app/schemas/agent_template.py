from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from enum import Enum

class RoleEnum(str, Enum):
    RESEARCH = "research"
    CODING = "coding"
    DATA_ANALYST = "data_analyst"
    CUSTOMER_SUPPORT = "customer_support"
    STRATEGIC_PLANNER = "strategic_planner"
    SECURITY_AUDITOR = "security_auditor"
    NEGOTIATOR = "negotiator"
    COORDINATOR = "coordinator"
    CUSTOM = "custom"

class AgentTemplateBase(BaseModel):
    name: str = Field(..., max_length=80)
    role: RoleEnum
    description: Optional[str] = Field(None, max_length=500)
    system_prompt: str = Field(..., max_length=2000)
    default_objective_template: Optional[str] = None
    default_tools: Optional[List[str]] = None
    default_resource_budget: Optional[Dict] = None
    default_trust_score: Optional[float] = None
    personality_traits: Optional[Dict] = None
    tags: Optional[List[str]] = None
    version: str = Field(default="1.0.0")
    is_public: bool = False

class AgentTemplateCreate(AgentTemplateBase):
    created_by: str

class AgentTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    default_objective_template: Optional[str] = None
    default_tools: Optional[List[str]] = None
    default_resource_budget: Optional[Dict] = None
    default_trust_score: Optional[float] = None
    personality_traits: Optional[Dict] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None

class AgentTemplateRead(AgentTemplateBase):
    id: str
    created_by: str
    use_count: int
    avg_performance_score: Optional[float]
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True
