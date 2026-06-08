
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
    
    # Evaluation Metrics (0-100 scale for rates and qualities)
    goals_completed: int = Field(default=0, description="Number of goals achieved")
    total_goals: int = Field(default=1, description="Total goals assigned (min 1 to avoid division by zero)")
    plan_quality: float = Field(default=100.0, description="Quality of plans generated (0-100)")
    reasoning_depth: float = Field(default=100.0, description="Depth of chain-of-thought (0-100)")
    
    alliance_count: int = Field(default=0, description="Number of active alliances")
    possible_alliances: int = Field(default=1, description="Total possible alliances (min 1)")
    avg_trust_given: float = Field(default=100.0, description="Average trust given to others (0-100)")
    resource_sharing_rate: float = Field(default=100.0, description="Rate of sharing resources (0-100)")
    
    failure_rate: float = Field(default=0.0, description="Failure rate (0-100)")
    deadline_hit_rate: float = Field(default=100.0, description="Rate of hitting deadlines (0-100)")
    hallucination_rate: float = Field(default=0.0, description="Hallucination rate (0-100)")
    
    resource_efficiency: float = Field(default=100.0, description="Resource utilization efficiency (0-100)")
    goal_completion_speed_normalized: float = Field(default=100.0, description="Normalized speed of goal completion (0-100)")
    waste_rate: float = Field(default=0.0, description="Rate of resource waste (0-100)")
    
    conflict_involvement_rate: float = Field(default=0.0, description="Rate of involvement in conflicts (0-100)")
    escalation_rate: float = Field(default=0.0, description="Rate of escalating issues (0-100)")
    failure_propagation_score: float = Field(default=0.0, description="Score for propagating failures (0-100)")

    def __hash__(self):
        return hash(self.id)
