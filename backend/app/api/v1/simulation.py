from fastapi import APIRouter

router = APIRouter()

@router.post("/simulation/start")
async def start_simulation():
    return {"status": "simulation started"}

@router.post("/simulation/stop")
async def stop_simulation():
    return {"status": "simulation stopped"}
