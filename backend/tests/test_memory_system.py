import pytest
from app.db.models import Base
from app.db.session import SessionLocal, engine
from app.db.models.relationship import AgentRelationship, RelationshipType
from app.memory.stm import ShortTermMemory
from app.memory.ltm import LongTermMemory, LTMItem
from app.memory.shared import SharedMemoryPool
from app.memory.episodic import EpisodicMemoryStore
from app.memory.manager import MemoryManager

import uuid

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_short_term_memory():
    stm = ShortTermMemory(max_items=3)
    # Add items
    stm.add("agent_1", "item_1", tick=1, importance=0.8)
    stm.add("agent_1", "item_2", tick=2, importance=0.5)
    stm.add("agent_1", "item_3", tick=3, importance=0.9)
    
    # Retrieve
    retrieved = stm.retrieve("agent_1", "item_2", tick=4)
    assert retrieved is not None
    assert retrieved.access_count == 1
    assert retrieved.last_access_tick == 4
    
    # Eviction: since max_items=3, adding a 4th should evict the least important.
    # item_2 was accessed so its importance decayed/accessed. Let's see:
    # item_1 (0.8), item_2 (0.5), item_3 (0.9).
    # Least important is item_2 (0.5).
    # But wait, let's run decay first.
    stm.decay(current_tick=5, decay_factor=0.95)
    # Now add a 4th item to trigger eviction.
    stm.add("agent_1", "item_4", tick=5, importance=1.0)
    
    # item_2 should be evicted because it had the lowest importance (0.5 * decay < others)
    assert stm.retrieve("agent_1", "item_2", tick=6) is None
    assert stm.retrieve("agent_1", "item_1", tick=6) is not None
    assert stm.retrieve("agent_1", "item_3", tick=6) is not None
    assert stm.retrieve("agent_1", "item_4", tick=6) is not None

def test_long_term_memory():
    # LongTermMemory should fall back to :memory: if Qdrant isn't running
    ltm = LongTermMemory(collection_name="test_collection", dim=4)
    item = LTMItem(
        content="AI alignment is crucial",
        embedding=[0.1, 0.2, 0.3, 0.4],
        tick_created=10,
        metadata={"source_agent_id": "agent_1"}
    )
    ltm.add_item(item)
    
    results = ltm.search(query_vector=[0.1, 0.2, 0.3, 0.4], top_k=1)
    assert len(results) == 1
    assert results[0].content == "AI alignment is crucial"

def test_shared_memory_pool(db_session):
    shared_pool = SharedMemoryPool(db_session)
    sim_uuid = uuid.uuid4()
    
    # Setup relationship: agent_a and agent_b are allied
    rel = AgentRelationship(
        simulation_id=sim_uuid,
        agent_a_id="agent_a",
        agent_b_id="agent_b",
        relationship_type=RelationshipType.allied,
        trust_score=0.8
    )
    db_session.add(rel)
    db_session.commit()
    
    # Write to shared memory pool (trust > 0.6 should succeed)
    item = shared_pool.write(
        simulation_id=sim_uuid,
        agent_id="agent_a",
        content="Shared plans for resource gathering",
        tags=["gathering", "alliance"],
        trust_score=0.8
    )
    assert item is not None
    assert item.version == 1
    
    # Try writing with low trust score (should fail/return None if allies exist and none have trust > 0.6)
    # Since we have rel in DB with trust_score = 0.8, we still have trust > 0.6 in DB.
    # Let's update DB trust_score to 0.4 to test failure
    rel.trust_score = 0.4
    db_session.commit()
    
    fail_item = shared_pool.write(
        simulation_id=sim_uuid,
        agent_id="agent_a",
        content="Secret alliance plot",
        tags=["plot"],
        trust_score=0.3
    )
    assert fail_item is None
    
    # Read open to all pool members (allies)
    # Let's restore trust and write successfully
    rel.trust_score = 0.7
    db_session.commit()
    shared_pool.write(
        simulation_id=sim_uuid,
        agent_id="agent_a",
        content="Updated plans",
        tags=["gathering"],
        trust_score=0.7
    )
    
    records = shared_pool.read(simulation_id=sim_uuid, agent_id="agent_b")
    assert len(records) > 0
    assert records[0].content == "Updated plans"

def test_episodic_memory_store(db_session):
    store = EpisodicMemoryStore(db_session)
    sim_uuid = uuid.uuid4()
    
    store.log(
        agent_id="agent_1",
        simulation_id=sim_uuid,
        tick=5,
        episode_type="conflict_resolution",
        context_snapshot={"resources": {"compute": 2}},
        outcome="successfully resolved resource contention",
        emotional_valence=0.5
    )
    
    # Query embedding [0.5, 0.5, 0.5, 0.5]
    query_emb = [0.5] * 1536
    results = store.recall(
        agent_id="agent_1",
        simulation_id=sim_uuid,
        query_embedding=query_emb,
        top_k=5
    )
    assert len(results) == 1
    assert results[0].episode_type == "conflict_resolution"
    assert results[0].context_snapshot == {"resources": {"compute": 2}}

def test_memory_manager():
    # Verify we can initialize MemoryManager and run through the layer operations
    manager = MemoryManager()
    manager.store_stm("agent_1", "Initial memory trace", tick=1, importance=0.9)
    
    # Access it to increase access count
    for _ in range(4):
        manager.stm.retrieve("agent_1", "Initial memory trace", tick=2)
        
    # Promote to LTM (should succeed because importance > 0.7 and access_count > 3)
    # Let's call promote_to_ltm
    manager.promote_to_ltm("agent_1")
    
    # Verify it is in LTM
    results = manager.retrieve_ltm("Initial memory trace", top_k=1)
    assert len(results) == 1
    assert results[0].content == "Initial memory trace"
