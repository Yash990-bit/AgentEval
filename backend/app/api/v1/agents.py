from fastapi import APIRouter, HTTPException
from typing import List
from uuid import uuid4
from pydantic import BaseModel

router = APIRouter()

# In‑memory store for demo purposes
_agents: dict[str, dict] = {}

class AgentCreate(BaseModel):
    name: str
    role: str
    objective: str

class AgentRead(BaseModel):
    id: str
    name: str
    role: str
    objective: str
    status: str = "idle"

@router.post("/agents", response_model=AgentRead)
async def create_agent(agent: AgentCreate):
    agent_id = str(uuid4())
    _agents[agent_id] = agent.dict()
    return AgentRead(id=agent_id, **agent.dict())

@router.get("/agents", response_model=List[AgentRead])
async def list_agents():
    return [AgentRead(id=aid, **adata) for aid, adata in _agents.items()]

@router.get("/agents/{agent_id}", response_model=AgentRead)
async def get_agent(agent_id: str):
    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentRead(id=agent_id, **_agents[agent_id])
