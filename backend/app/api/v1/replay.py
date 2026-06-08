from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID
import msgpack
import asyncio

from ...services.replay_engine import ReplayEngine
from ...models.simulation_snapshot import SimulationSnapshot
from ...utils.s3_client import S3Client
from ...dependencies import get_db, get_s3_client

router = APIRouter(prefix="/simulations/{simulation_id}/replay", tags=["replay"])

@router.get("/ticks", response_model=dict)
def get_tick_range(
    simulation_id: UUID,
    db: Session = Depends(get_db)
):
    """Return the min, max, and total snapshot counts for a simulation."""
    engine = ReplayEngine(db=db, s3=get_s3_client())
    return engine.get_tick_range(simulation_id)

@router.get("/snapshot/{tick}")
def get_snapshot(
    simulation_id: UUID,
    tick: int,
    db: Session = Depends(get_db)
):
    """Fetch a snapshot and return JSON representation."""
    engine = ReplayEngine(db=db, s3=get_s3_client())
    data = engine.load_snapshot(simulation_id, tick)
    return JSONResponse(content=data)

@router.get("/diff")
def get_diff(
    simulation_id: UUID,
    from_tick: int,
    to_tick: int,
    db: Session = Depends(get_db)
):
    """Return the diff between two snapshots."""
    engine = ReplayEngine(db=db, s3=get_s3_client())
    return engine.get_diff(simulation_id, from_tick, to_tick)

@router.websocket("/stream")
async def stream_snapshots(
    websocket: WebSocket,
    simulation_id: UUID,
    from_tick: int = 0,
    to_tick: int = 0,
    speed: int = 1
):
    """Stream snapshots over WebSocket at the requested speed.

    Parameters:
        from_tick: start tick (inclusive). If 0, start from earliest.
        to_tick: end tick (inclusive). If 0, stream to latest.
        speed: multiplier (1 = real‑time, 2 = 2×, etc.).
    """
    await websocket.accept()
    engine = ReplayEngine(db=get_db(), s3=get_s3_client())
    # Determine range
    range_info = engine.get_tick_range(simulation_id)
    start = from_tick or range_info["min_tick"]
    end = to_tick or range_info["max_tick"]
    if start > end:
        await websocket.close(code=1008)
        return
    try:
        for tick in range(start, end + 1):
            snapshot = engine.load_snapshot(simulation_id, tick)
            packed = msgpack.packb(snapshot, use_bin_type=True)
            await websocket.send_bytes(packed)
            await asyncio.sleep(1 / speed)
    except WebSocketDisconnect:
        pass
    finally:
        await websocket.close()
