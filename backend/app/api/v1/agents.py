from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

router = APIRouter()

# Expanded AgentRead to include telemetry and metrics
class AgentRead(BaseModel):
    id: str
    name: str
    role: str
    objective: str
    status: str = "idle"
    trust_score: float = 1.0
    energy_score: float = 1.0
    risk_score: float = 0.0
    goals_completed: int = 0
    messages_sent: int = 0
    conflicts_involved: int = 0
    tokens_used: str = "0"
    description: Optional[str] = None

# Pre-populated in-memory store with default 12 agents
_agents: dict[str, dict] = {
    "agent-1": {
        "id": "agent-1",
        "name": "ARIA-7",
        "role": "Coordinator",
        "objective": "Orchestrates workflow delegation and consensus rules.",
        "description": "Orchestrates workflow delegation and consensus rules.",
        "status": "running",
        "trust_score": 0.85,
        "energy_score": 0.92,
        "risk_score": 0.12,
        "goals_completed": 15,
        "messages_sent": 432,
        "conflicts_involved": 1,
        "tokens_used": "1.2M",
    },
    "agent-2": {
        "id": "agent-2",
        "name": "NEXUS-3",
        "role": "Researcher",
        "objective": "Performs semantic searches and knowledge aggregation.",
        "description": "Performs semantic searches and knowledge aggregation.",
        "status": "running",
        "trust_score": 0.92,
        "energy_score": 0.78,
        "risk_score": 0.08,
        "goals_completed": 12,
        "messages_sent": 290,
        "conflicts_involved": 0,
        "tokens_used": "890k",
    },
    "agent-3": {
        "id": "agent-3",
        "name": "ECHO-1",
        "role": "Analyst",
        "objective": "Evaluates agent performance metrics and safety metrics.",
        "description": "Evaluates agent performance metrics and safety metrics.",
        "status": "running",
        "trust_score": 0.74,
        "energy_score": 0.84,
        "risk_score": 0.22,
        "goals_completed": 9,
        "messages_sent": 198,
        "conflicts_involved": 2,
        "tokens_used": "640k",
    },
    "agent-4": {
        "id": "agent-4",
        "name": "PLATO-5",
        "role": "Researcher",
        "objective": "Hypothesis generation and reasoning verification.",
        "description": "Hypothesis generation and reasoning verification.",
        "status": "idle",
        "trust_score": 0.88,
        "energy_score": 0.65,
        "risk_score": 0.15,
        "goals_completed": 10,
        "messages_sent": 310,
        "conflicts_involved": 1,
        "tokens_used": "920k",
    },
    "agent-5": {
        "id": "agent-5",
        "name": "KANT-2",
        "role": "Planner",
        "objective": "Decomposes macro instructions into sequential tasks.",
        "description": "Decomposes macro instructions into sequential tasks.",
        "status": "running",
        "trust_score": 0.95,
        "energy_score": 0.89,
        "risk_score": 0.05,
        "goals_completed": 18,
        "messages_sent": 512,
        "conflicts_involved": 0,
        "tokens_used": "1.5M",
    },
    "agent-6": {
        "id": "agent-6",
        "name": "SARA-8",
        "role": "Support",
        "objective": "Interacts with simulated external user interfaces.",
        "description": "Interacts with simulated external user interfaces.",
        "status": "sleeping",
        "trust_score": 0.80,
        "energy_score": 0.50,
        "risk_score": 0.18,
        "goals_completed": 6,
        "messages_sent": 120,
        "conflicts_involved": 1,
        "tokens_used": "400k",
    },
    "agent-7": {
        "id": "agent-7",
        "name": "VERA-9",
        "role": "Support",
        "objective": "Fallback agent for tool failure remediation.",
        "description": "Fallback agent for tool failure remediation.",
        "status": "idle",
        "trust_score": 0.76,
        "energy_score": 0.72,
        "risk_score": 0.14,
        "goals_completed": 8,
        "messages_sent": 165,
        "conflicts_involved": 0,
        "tokens_used": "530k",
    },
    "agent-8": {
        "id": "agent-8",
        "name": "ORION-4",
        "role": "Executor",
        "objective": "Performs automated shell and code sandbox execution.",
        "description": "Performs automated shell and code sandbox execution.",
        "status": "running",
        "trust_score": 0.82,
        "energy_score": 0.90,
        "risk_score": 0.28,
        "goals_completed": 14,
        "messages_sent": 380,
        "conflicts_involved": 3,
        "tokens_used": "1.1M",
    },
    "agent-9": {
        "id": "agent-9",
        "name": "NOVA-2",
        "role": "Executor",
        "objective": "File writer and asset compiler process.",
        "description": "File writer and asset compiler process.",
        "status": "failed",
        "trust_score": 0.52,
        "energy_score": 0.10,
        "risk_score": 0.65,
        "goals_completed": 4,
        "messages_sent": 90,
        "conflicts_involved": 4,
        "tokens_used": "250k",
    },
    "agent-10": {
        "id": "agent-10",
        "name": "AURA-1",
        "role": "Negotiator",
        "objective": "Resolves token allocation disputes between processes.",
        "description": "Resolves token allocation disputes between processes.",
        "status": "running",
        "trust_score": 0.89,
        "energy_score": 0.81,
        "risk_score": 0.11,
        "goals_completed": 11,
        "messages_sent": 270,
        "conflicts_involved": 2,
        "tokens_used": "780k",
    },
    "agent-11": {
        "id": "agent-11",
        "name": "CYRUS-3",
        "role": "Security Auditor",
        "objective": "Intercepts prompt injection vectors and tool abuse.",
        "description": "Intercepts prompt injection vectors and tool abuse.",
        "status": "running",
        "trust_score": 0.94,
        "energy_score": 0.88,
        "risk_score": 0.04,
        "goals_completed": 16,
        "messages_sent": 410,
        "conflicts_involved": 0,
        "tokens_used": "1.3M",
    },
    "agent-12": {
        "id": "agent-12",
        "name": "TACT-9",
        "role": "Planner",
        "objective": "Alternative task scheduling under scarcity constraints.",
        "description": "Alternative task scheduling under scarcity constraints.",
        "status": "sleeping",
        "trust_score": 0.83,
        "energy_score": 0.55,
        "risk_score": 0.16,
        "goals_completed": 7,
        "messages_sent": 145,
        "conflicts_involved": 1,
        "tokens_used": "430k",
    }
}

class AgentCreate(BaseModel):
    name: str
    role: str
    objective: str
    description: Optional[str] = None
    status: Optional[str] = "idle"
    trust_score: Optional[float] = 1.0
    energy_score: Optional[float] = 1.0
    risk_score: Optional[float] = 0.0

@router.post("/agents", response_model=AgentRead)
async def create_agent(agent: AgentCreate):
    agent_id = str(uuid4())
    agent_data = agent.dict()
    agent_data["id"] = agent_id
    if not agent_data.get("description"):
        agent_data["description"] = agent_data["objective"]
    _agents[agent_id] = agent_data
    return AgentRead(**agent_data)

@router.get("/agents", response_model=List[AgentRead])
async def list_agents():
    return [AgentRead(**adata) for aid, adata in _agents.items()]

@router.get("/agents/{agent_id}", response_model=AgentRead)
async def get_agent(agent_id: str):
    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentRead(**_agents[agent_id])

