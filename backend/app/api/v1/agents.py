from fastapi import APIRouter
from typing import List

router = APIRouter()

# Placeholder in‑memory store
_agents: List[dict] = []

@router.get("/agents")
async def list_agents():
    return {"agents": _agents}

@router.post("/agents")
async def create_agent(agent: dict):
    _agents.append(agent)
    return {"msg": "agent created", "agent": agent}

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    for a in _agents:
        if a.get("id") == agent_id:
            return a
    return {"error": "not found"}
