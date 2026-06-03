import pytest
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.conflict.severity import compute_severity
from app.conflict.detector import ConflictDetector
from app.conflict.models import Conflict, ConflictType, ConflictStatus
from app.graph.agent_graph import AgentGraph, AgentGraphNode
from app.graph.agent_state import AgentState
from app.db.session import SessionLocal, engine
from app.db.models import Base

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
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

def test_severity_score_computation():
    # severity = (0.4 × resource_impact) + (0.3 × goal_criticality) + (0.2 × trust_damage) + (0.1 × spread_factor)
    # spread_factor = 2 / 5 = 0.4
    # severity = (0.4 * 0.5) + (0.3 * 0.8) + (0.2 * 0.6) + (0.1 * 0.4)
    # severity = 0.2 + 0.24 + 0.12 + 0.04 = 0.6
    score = compute_severity(
        resource_impact=0.5,
        goal_criticality=0.8,
        trust_damage=0.6,
        agents_affected=2,
        total_agents=5
    )
    assert score == pytest.approx(0.60)

    # Clamping test: severity above 1.0 gets clamped to 1.0
    score_clamped = compute_severity(
        resource_impact=1.0,
        goal_criticality=1.0,
        trust_damage=1.0,
        agents_affected=10,
        total_agents=10
    )
    assert score_clamped == pytest.approx(1.0)

def test_deadlock_detection():
    sim_id = str(uuid.uuid4())
    graph = AgentGraph(simulation_id=sim_id)
    
    # Setup agents with circular wait: agent_1 waiting for agent_2, agent_2 waiting for agent_1
    node_1 = AgentGraphNode("agent_1")
    node_1.state.waiting_for = ["agent_2"]
    node_2 = AgentGraphNode("agent_2")
    node_2.state.waiting_for = ["agent_1"]
    
    graph.agents["agent_1"] = node_1
    graph.agents["agent_2"] = node_2

    # Run detection
    db = SessionLocal()
    try:
        detector = ConflictDetector(db_session=db, graph=graph)
        conflicts = detector._detect_deadlock(tick=1)
        
        assert len(conflicts) == 1
        conflict = conflicts[0]
        assert conflict.conflict_type == ConflictType.DEADLOCK
        assert set(conflict.agents_involved) == {"agent_1", "agent_2"}
        assert "Circular waiting detected" in conflict.root_cause
    finally:
        db.close()

def test_goal_conflict_detection():
    sim_id = str(uuid.uuid4())
    graph = AgentGraph(simulation_id=sim_id)
    
    # Setup agents with exclusive goals (using fallback Jaccard keyword matching since Jaccard sim will be 0.0 < 0.3)
    node_1 = AgentGraphNode("agent_1")
    node_1.state.goal_stack = [{"description": "maximize compute speed"}]
    node_2 = AgentGraphNode("agent_2")
    node_2.state.goal_stack = [{"description": "save battery power completely"}]
    
    graph.agents["agent_1"] = node_1
    graph.agents["agent_2"] = node_2

    db = SessionLocal()
    try:
        detector = ConflictDetector(db_session=db, graph=graph)
        conflicts = detector._detect_goal_conflict(tick=1)
        
        assert len(conflicts) == 1
        conflict = conflicts[0]
        assert conflict.conflict_type == ConflictType.GOAL
        assert set(conflict.agents_involved) == {"agent_1", "agent_2"}
    finally:
        db.close()

def test_resource_conflict_resolution():
    from app.config import RESOURCE_CAPACITY
    sim_id = str(uuid.uuid4())
    graph = AgentGraph(simulation_id=sim_id)
    
    # 3 agents all requesting 'compute_units' which has capacity = 5
    # Priorities: A (coordinator = 3.0), B (executor = 2.5), C (support = 1.0)
    # Total priority = 6.5
    # Total capacity = 2.0 (dynamically override)
    node_a = AgentGraphNode("agent_a")
    node_a.role = "coordinator"
    node_a.state.resource_requests = ["compute_units"]
    
    node_b = AgentGraphNode("agent_b")
    node_b.role = "executor"
    node_b.state.resource_requests = ["compute_units"]
    
    node_c = AgentGraphNode("agent_c")
    node_c.role = "support"
    node_c.state.resource_requests = ["compute_units"]

    graph.agents["agent_a"] = node_a
    graph.agents["agent_b"] = node_b
    graph.agents["agent_c"] = node_c

    original_capacity = RESOURCE_CAPACITY.get("compute_units", 5)
    RESOURCE_CAPACITY["compute_units"] = 2

    db = SessionLocal()
    try:
        detector = ConflictDetector(db_session=db, graph=graph)
        conflicts = detector.detect(tick=1)
        
        # Verify a resource conflict was detected
        res_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.RESOURCE]
        assert len(res_conflicts) == 1
        conflict = res_conflicts[0]
        
        # Verify status is AUTO_RESOLVED
        assert conflict.status == ConflictStatus.AUTO_RESOLVED
        
        # Verify allocations were written to the state (priority weighted)
        # agent_a = (3.0 / 6.5) * 2 = 0.92
        # agent_b = (2.5 / 6.5) * 2 = 0.77
        # agent_c = (1.0 / 6.5) * 2 = 0.31
        assert graph.agents["agent_a"].state.resource_budget["compute_units"] == pytest.approx(0.92)
        assert graph.agents["agent_b"].state.resource_budget["compute_units"] == pytest.approx(0.77)
        assert graph.agents["agent_c"].state.resource_budget["compute_units"] == pytest.approx(0.31)
    finally:
        RESOURCE_CAPACITY["compute_units"] = original_capacity
        db.close()

def test_conflict_api_endpoints(db_session):
    sim_id = str(uuid.uuid4())
    
    # Seed a conflict in the database
    conflict_id = uuid.uuid4()
    c = Conflict(
        id=conflict_id,
        simulation_id=uuid.UUID(sim_id),
        conflict_type=ConflictType.TRUST,
        detected_at_tick=5,
        agents_involved=["agent_x", "agent_y"],
        severity_score=0.45,
        root_cause="Test trust break",
        suggested_resolution="Mediate",
        status=ConflictStatus.ACTIVE
    )
    db_session.add(c)
    db_session.commit()

    # Test GET /api/v1/simulations/{id}/conflicts
    response = client.get(f"/api/v1/simulations/{sim_id}/conflicts")
    assert response.status_code == 200
    conflicts = response.json()
    assert len(conflicts) == 1
    assert conflicts[0]["id"] == str(conflict_id)
    assert conflicts[0]["conflict_type"] == "Trust Breakdown"

    # Test GET /api/v1/conflicts/{id}
    response_single = client.get(f"/api/v1/conflicts/{conflict_id}")
    assert response_single.status_code == 200
    data = response_single.json()
    assert data["id"] == str(conflict_id)
    assert data["severity_score"] == 0.45
