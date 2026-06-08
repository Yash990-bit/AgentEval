import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import msgpack

from ..utils.s3_client import S3Client
from ..models.simulation_snapshot import SimulationSnapshot

def record_snapshot(
    db: Session,
    s3: S3Client,
    simulation_id: uuid.UUID,
    tick: int,
    snapshot: Dict[str, Any]
) -> None:
    """Serialize a snapshot with MessagePack, upload to S3, and index in DB.

    Args:
        db: SQLAlchemy session.
        s3: Configured S3 client.
        simulation_id: Identifier of the simulation run.
        tick: Simulation tick number.
        snapshot: Full snapshot dict (including agents, resources, etc.).
    """
    # Serialize to MessagePack binary
    data = msgpack.packb(snapshot, use_bin_type=True)
    # S3 key pattern
    key = f"simulations/{simulation_id}/snapshots/{tick:05d}.msgpack"
    # Upload binary
    s3.upload_snapshot(key, data)
    # Insert DB record
    entry = SimulationSnapshot(
        simulation_id=simulation_id,
        tick=tick,
        s3_key=key,
        size_bytes=len(data),
        created_at=datetime.utcnow()
    )
    db.add(entry)
    db.commit()
