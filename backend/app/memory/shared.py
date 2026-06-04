# backend/app/memory/shared.py
"""Shared Memory Pool helper.
Handles per-alliance shared memories with trust score checks and versioning.
"""

from typing import List, Any
from sqlalchemy import func
from app.db.models.relationship import AgentRelationship, RelationshipType
from app.models.shared_memory import SharedMemory

class SharedMemoryPool:
    def __init__(self, db_session):
        self.db = db_session

    def write(self, simulation_id: Any, agent_id: str, content: str, tags: List[str], trust_score: float = None) -> SharedMemory | None:
        """Write to shared memory pool.
        Requires trust_score > 0.6 with at least one pool member (allied agent).
        Each write creates a new record with an incremental version number.
        """
        # Find all allied agents of agent_id in this simulation
        # Note: simulation_id can be UUID or string, cast as string for DB query compatibility if needed, or query as is.
        sim_id_str = str(simulation_id)
        
        allies = self.db.query(AgentRelationship).filter(
            AgentRelationship.simulation_id == simulation_id,
            AgentRelationship.relationship_type == RelationshipType.allied,
            ((AgentRelationship.agent_a_id == agent_id) | (AgentRelationship.agent_b_id == agent_id))
        ).all()

        # Check if we have trust > 0.6 with at least one pool member (ally).
        # We check both the passed trust_score and the trust_score in the database relationships.
        has_trust = False
        if trust_score is not None and trust_score > 0.6:
            has_trust = True
        else:
            for rel in allies:
                if rel.trust_score > 0.6:
                    has_trust = True
                    break
        
        # If there are pool members, we enforce the trust check. If there are no pool members, write is allowed/created.
        if allies and not has_trust:
            # Cannot write due to insufficient trust
            return None

        # Determine version (incremented per simulation_id, agent_id, content)
        max_version = self.db.query(func.max(SharedMemory.version)).filter(
            SharedMemory.simulation_id == simulation_id,
            SharedMemory.agent_id == agent_id,
            SharedMemory.content == content
        ).scalar() or 0

        new_item = SharedMemory(
            simulation_id=simulation_id,
            agent_id=agent_id,
            content=content,
            tags=tags,
            version=max_version + 1
        )
        self.db.add(new_item)
        self.db.commit()
        self.db.refresh(new_item)
        return new_item

    def read(self, simulation_id: Any, agent_id: str) -> List[SharedMemory]:
        """Read shared memory. Returns all records accessible to pool members (allies of agent_id).
        """
        # Find all allied agents of agent_id in this simulation
        allies = self.db.query(AgentRelationship).filter(
            AgentRelationship.simulation_id == simulation_id,
            AgentRelationship.relationship_type == RelationshipType.allied,
            ((AgentRelationship.agent_a_id == agent_id) | (AgentRelationship.agent_b_id == agent_id))
        ).all()

        # Build list of agent IDs in the pool (the agent itself + its allies)
        pool_agent_ids = {agent_id}
        for rel in allies:
            pool_agent_ids.add(rel.agent_a_id)
            pool_agent_ids.add(rel.agent_b_id)

        # Query all shared memories written by any pool member in this simulation
        records = self.db.query(SharedMemory).filter(
            SharedMemory.simulation_id == simulation_id,
            SharedMemory.agent_id.in_(list(pool_agent_ids))
        ).order_by(SharedMemory.id.desc()).all()

        return records
