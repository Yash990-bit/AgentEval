# backend/app/services/replay_engine.py

import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
import msgpack
from deepdiff import DeepDiff

from ..models.simulation_snapshot import SimulationSnapshot
from ..utils.s3_client import S3Client

class ReplayEngine:
    def __init__(self, db: Session, s3: S3Client):
        self.db = db
        self.s3 = s3

    def load_snapshot(self, simulation_id: uuid.UUID, tick: int) -> Dict[str, Any]:
        """Fetch a snapshot from S3 and deserialize it."""
        entry = (
            self.db.query(SimulationSnapshot)
            .filter_by(simulation_id=simulation_id, tick=tick)
            .first()
        )
        if not entry:
            raise ValueError(f"Snapshot not found for tick {tick}")
        raw = self.s3.download_snapshot(entry.s3_key)
        return msgpack.unpackb(raw, raw=False)

    def get_tick_range(self, simulation_id: uuid.UUID) -> Dict[str, int]:
        q = self.db.query(SimulationSnapshot).filter_by(simulation_id=simulation_id)
        min_tick = q.with_entities(func.min(SimulationSnapshot.tick)).scalar() or 0
        max_tick = q.with_entities(func.max(SimulationSnapshot.tick)).scalar() or 0
        total = q.count()
        return {"min_tick": min_tick, "max_tick": max_tick, "total_snapshots": total}

    def get_diff(self, simulation_id: uuid.UUID, tick_a: int, tick_b: int) -> Dict[str, Any]:
        snap_a = self.load_snapshot(simulation_id, tick_a)
        snap_b = self.load_snapshot(simulation_id, tick_b)
        diff = DeepDiff(snap_a, snap_b, ignore_order=True).to_dict()
        return diff
