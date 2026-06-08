# backend/app/models/simulation_snapshot.py

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.models import Base
import uuid

class SimulationSnapshot(Base):
    __tablename__ = "simulation_snapshots"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tick = Column(Integer, nullable=False)
    s3_key = Column(String, nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # Ensure one snapshot per tick per simulation
        # Unique constraint (simulation_id, tick)
        {'postgresql_partition_by': None},
    )
