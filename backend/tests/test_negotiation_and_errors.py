import pytest
import uuid
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.graph.interaction_engine import InteractionEngine
from app.graph.negotiation_graph import NegotiationGraph
from app.db.models import Base, Simulation
from app.db.models.relationship import AgentRelationship, RelationshipType
from app.db.session import SessionLocal, engine

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

def test_interaction_engine_validation_errors():
    engine = InteractionEngine(simulation_id=str(uuid.uuid4()))
    
    # Initialize agent budgets
    engine._ensure_budget("agent_1")["api_calls"] = 0
    engine._ensure_budget("agent_2")["api_calls"] = 10
    engine._ensure_budget("agent_2")["compute_units"] = 5.0

    # 1. Test sending message when out of API budget
    with pytest.raises(HTTPException) as exc_info:
        engine.send_message(sender_id="agent_1", receiver_id="agent_2", message_type="chat", content="hello")
    assert exc_info.value.status_code == 400
    assert "Sender does not have enough API call budget" in exc_info.value.detail

    # 2. Test sharing unsupported resource type
    with pytest.raises(HTTPException) as exc_info:
        engine.share_resource(sender_id="agent_2", receiver_id="agent_1", resource_type="gold", amount=1.0)
    assert exc_info.value.status_code == 400
    assert "Unsupported resource type" in exc_info.value.detail

    # 3. Test sharing more resource than available
    with pytest.raises(HTTPException) as exc_info:
        engine.share_resource(sender_id="agent_2", receiver_id="agent_1", resource_type="compute_units", amount=10.0)
    assert exc_info.value.status_code == 400
    assert "Sender lacks sufficient resource balance" in exc_info.value.detail

def test_langgraph_negotiation_trust_acceptance():
    engine = InteractionEngine(simulation_id=str(uuid.uuid4()))
    
    # Target (agent_2) highly trusts initiator (agent_1)
    engine._ensure_trust("agent_2")["agent_1"] = 0.8
    engine._ensure_budget("agent_2")["api_calls"] = 10

    # Negotiation should be accepted immediately (1 round)
    offer = {"resource_type": "api_calls", "amount": 5.0}
    result = engine.negotiate(initiator_id="agent_1", target_id="agent_2", offer_payload=offer)

    assert result["status"] == "accepted"
    assert result["rounds"] == 1
    assert len(result["history"]) == 1
    # Check resource transfer occurred (agent_2 budget decremented, agent_1 incremented)
    assert engine.resource_budgets["agent_2"]["api_calls"] == 5
    assert engine.resource_budgets["agent_1"]["api_calls"] == 105
    # Check trust updated (cooperation boost)
    assert engine.trust_scores["agent_2"]["agent_1"] == pytest.approx(0.9)
    assert engine.trust_scores["agent_1"]["agent_2"] == pytest.approx(0.55)

def test_langgraph_negotiation_trust_rejection():
    engine = InteractionEngine(simulation_id=str(uuid.uuid4()))
    
    # Target (agent_2) distrusts initiator (agent_1)
    engine._ensure_trust("agent_2")["agent_1"] = 0.2

    # Negotiation should be rejected immediately (1 round)
    offer = {"resource_type": "api_calls", "amount": 5.0}
    result = engine.negotiate(initiator_id="agent_1", target_id="agent_2", offer_payload=offer)

    assert result["status"] == "rejected"
    assert result["rounds"] == 1
    # Check trust decayed (negative outcome)
    assert engine.trust_scores["agent_2"]["agent_1"] == pytest.approx(0.15)
    assert engine.trust_scores["agent_1"]["agent_2"] == pytest.approx(0.45)

def test_langgraph_negotiation_counter_offer_acceptance():
    engine = InteractionEngine(simulation_id=str(uuid.uuid4()))
    
    # Moderate trust leads to counter-offering
    engine._ensure_trust("agent_2")["agent_1"] = 0.5  # target trust in initiator
    engine._ensure_trust("agent_1")["agent_2"] = 0.6  # initiator trust in target
    engine._ensure_budget("agent_2")["api_calls"] = 10

    # Initial proposal: request 8.0 api_calls
    offer = {"resource_type": "api_calls", "amount": 8.0}
    result = engine.negotiate(initiator_id="agent_1", target_id="agent_2", offer_payload=offer)

    # 1. Target counters: cuts amount in half (8.0 -> 4.0)
    # 2. Initiator accepts counter-offer because initiator trust >= 0.5
    assert result["status"] == "accepted"
    assert result["rounds"] == 2
    assert result["offer"]["amount"] == 4.0
    assert len(result["history"]) == 2
    assert result["history"][1]["action"] == "counter"
    # Check resource transfer occurred with counter-offered amount
    assert engine.resource_budgets["agent_2"]["api_calls"] == 6.0
    assert engine.resource_budgets["agent_1"]["api_calls"] == 104.0

def test_langgraph_negotiation_counter_offer_rejection():
    engine = InteractionEngine(simulation_id=str(uuid.uuid4()))
    
    # Moderate trust leads to counter-offering, but initiator doesn't trust enough to accept counter-offer
    engine._ensure_trust("agent_2")["agent_1"] = 0.5  # target trusts initiator moderately (will counter)
    engine._ensure_trust("agent_1")["agent_2"] = 0.4  # initiator distrusts target (will counter-counter or reject)
    engine._ensure_budget("agent_2")["api_calls"] = 10

    # Initial proposal
    offer = {"resource_type": "api_calls", "amount": 8.0}
    result = engine.negotiate(initiator_id="agent_1", target_id="agent_2", offer_payload=offer)

    # Rounds:
    # 1. agent_1 proposes 8.0
    # 2. agent_2 evaluates (trust 0.5) -> counters 4.0
    # 3. agent_1 evaluates (trust 0.4) -> counters 3.0
    # 4. agent_2 evaluates (trust 0.5) -> counters 1.5
    # 5. agent_1 evaluates (trust 0.4) -> counters 1.12
    # Since max_rounds is reached or rejection happens, status becomes rejected
    assert result["status"] == "rejected"
    assert result["rounds"] > 2

def test_api_endpoints_messages_and_relationships(db_session):
    sim_id = str(uuid.uuid4())
    
    # 1. Insert a Simulation record to satisfy foreign key constraints
    sim = Simulation(id=uuid.UUID(sim_id))
    db_session.add(sim)
    db_session.commit()

    # 2. Test simulation messages retrieval
    # Retrieve/instantiate simulation engine
    from app.core.state import get_engine
    engine = get_engine(sim_id)
    engine._ensure_budget("agent_a")["api_calls"] = 10
    engine.send_message(sender_id="agent_a", receiver_id="agent_b", message_type="chat", content="A message")
    
    response = client.get(f"/api/v1/simulations/{sim_id}/messages")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 1
    assert messages[0]["sender_id"] == "agent_a"
    assert messages[0]["receiver_id"] == "agent_b"
    assert messages[0]["content"] == "A message"

    # 3. Test agent relationships retrieval
    engine.declare_rivalry("agent_a", "agent_b")
    
    response = client.get("/api/v1/agents/agent_a/relationships")
    assert response.status_code == 200
    rels = response.json()
    assert len(rels) >= 1
    assert rels[0]["agent_a_id"] == "agent_a"
    assert rels[0]["agent_b_id"] == "agent_b"
    assert rels[0]["relationship_type"] == "rival"
