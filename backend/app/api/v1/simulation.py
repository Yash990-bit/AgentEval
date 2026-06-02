from fastapi import APIRouter
from typing import Any, Dict

router = APIRouter()

# Simple in‑memory simulation state
_simulation_state: Dict[str, Any] = {"running": False, "step": 0}

@router.get("/simulation")
async def get_simulation_status():
    return {"status": "running" if _simulation_state["running"] else "stopped", "step": _simulation_state["step"]}

@router.post("/simulation/start")
async def start_simulation():
    _simulation_state["running"] = True
    _simulation_state["step"] = 0
    return {"msg": "simulation started"}

@router.post("/simulation/stop")
async def stop_simulation():
    _simulation_state["running"] = False
    return {"msg": "simulation stopped"}

@router.post("/simulation/step")
async def advance_step():
    if _simulation_state["running"]:
        _simulation_state["step"] += 1
        return {"msg": "step advanced", "step": _simulation_state["step"]}
    return {"error": "simulation not running"}
