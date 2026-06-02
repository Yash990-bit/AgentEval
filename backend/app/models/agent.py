
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Agent(BaseModel):
    """Core representation of an AI agent in the simulation."""
    id: str = Field(..., description="Unique identifier for the agent")
    name: str = Field(..., description="Human‑readable name")
    role: str = Field(..., description="High‑level role, e.g., planner, executor")
    objective: str = Field(..., description="Goal the agent tries to achieve")
    memory: List[Dict] = Field(default_factory=list, description="Agent's episodic memory")
    tools: List[str] = Field(default_factory=list, description="Available tool names")
    resource_budget: float = Field(default=100.0, description="Total resources the agent can spend")
    trust_score: float = Field(default=1.0, ge=0.0, le=1.0, description="How much other agents trust this one")
    energy_score: float = Field(default=100.0, description="Current energy level")
    risk_score: float = Field(default=0.0, description="Risk tolerance (0‑1)")

    def __hash__(self):
        return hash(self.id)
