"""Tests for the Trust Network system.

Covers:
- Trust change rules (cooperation, betrayal, etc.)
- 3-hop trust propagation
- Trust decay after 15 idle ticks
- Reputation and influence calculation
- API endpoints for trust-network and trust-history
"""

import pytest
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.models.trust import AgentTrustEdge
from app.services.trust_engine import TrustEngine


@pytest.fixture(scope="module")
def test_engine():
    """Create an in-memory SQLite engine for tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_engine):
    """Provide a transactional DB session for each test."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def trust_engine(db_session):
    return TrustEngine(db_session)


SIM_ID = str(uuid.uuid4())
AGENT_A = "agent-alpha"
AGENT_B = "agent-beta"
AGENT_C = "agent-gamma"


# ---------------------------------------------------------------
# Trust change rules
# ---------------------------------------------------------------

class TestTrustChangeRules:
    def test_cooperation_success_increases_trust(self, trust_engine):
        trust_engine.apply_event(SIM_ID, AGENT_A, AGENT_B, "cooperation_success", tick=1)
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=SIM_ID,
            source_agent_id=AGENT_A,
            target_agent_id=AGENT_B,
        ).first()
        assert edge is not None
        assert edge.trust_score == pytest.approx(0.05)
        assert edge.last_updated_tick == 1
        assert len(edge.history) == 1
        assert edge.history[0]["tick"] == 1

    def test_message_accepted_increases_trust(self, trust_engine):
        sim = str(uuid.uuid4())
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "message_accepted", tick=1)
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        assert edge.trust_score == pytest.approx(0.03)

    def test_resource_shared_increases_trust(self, trust_engine):
        sim = str(uuid.uuid4())
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "resource_shared", tick=1)
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        assert edge.trust_score == pytest.approx(0.08)

    def test_alliance_formed_increases_trust(self, trust_engine):
        sim = str(uuid.uuid4())
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "alliance_formed", tick=1)
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        assert edge.trust_score == pytest.approx(0.10)

    def test_betrayal_decreases_trust(self, trust_engine):
        sim = str(uuid.uuid4())
        # Start with some trust
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "alliance_formed", tick=1)  # +0.10
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "cooperation_success", tick=2)  # +0.05
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "cooperation_success", tick=3)  # +0.05
        # Now betray: -0.30
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "betrayal", tick=4)
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        # 0.10 + 0.05 + 0.05 - 0.30 = -0.10 -> clamped to 0.0
        assert edge.trust_score == pytest.approx(0.0)

    def test_deception_detected_decreases_trust(self, trust_engine):
        sim = str(uuid.uuid4())
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "alliance_formed", tick=1)  # +0.10
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "deception_detected", tick=2)  # -0.20
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        # 0.10 - 0.20 = -0.10 -> clamped to 0.0
        assert edge.trust_score == pytest.approx(0.0)

    def test_resource_conflict_decreases_trust(self, trust_engine):
        sim = str(uuid.uuid4())
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "alliance_formed", tick=1)  # +0.10
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "resource_shared", tick=2)  # +0.08
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "resource_conflict", tick=3)  # -0.15
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        assert edge.trust_score == pytest.approx(0.03)

    def test_trust_score_clamped_at_one(self, trust_engine):
        sim = str(uuid.uuid4())
        # Apply many positive events to exceed 1.0
        for tick in range(1, 15):
            trust_engine.apply_event(sim, AGENT_A, AGENT_B, "alliance_formed", tick=tick)
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        assert edge.trust_score == pytest.approx(1.0)

    def test_unknown_event_type_raises(self, trust_engine):
        sim = str(uuid.uuid4())
        with pytest.raises(ValueError, match="Unknown trust event type"):
            trust_engine.apply_event(sim, AGENT_A, AGENT_B, "alien_invasion", tick=1)

    def test_history_accumulates(self, trust_engine):
        sim = str(uuid.uuid4())
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "cooperation_success", tick=1)
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "message_accepted", tick=2)
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "resource_shared", tick=3)
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        assert len(edge.history) == 3
        assert edge.history[0]["tick"] == 1
        assert edge.history[1]["tick"] == 2
        assert edge.history[2]["tick"] == 3


# ---------------------------------------------------------------
# Trust propagation (3-hop)
# ---------------------------------------------------------------

class TestTrustPropagation:
    def test_propagation_creates_ambient_trust(self, trust_engine):
        sim = str(uuid.uuid4())
        # A trusts B (> 0.6)
        for tick in range(1, 8):
            trust_engine.apply_event(sim, AGENT_A, AGENT_B, "alliance_formed", tick=tick)
        # B trusts C (> 0.6)
        for tick in range(1, 8):
            trust_engine.apply_event(sim, AGENT_B, AGENT_C, "alliance_formed", tick=tick)

        ab_edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        bc_edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_B, target_agent_id=AGENT_C
        ).first()
        assert ab_edge.trust_score > 0.6
        assert bc_edge.trust_score > 0.6

        # Propagate
        trust_engine.propagate_trust(sim)

        # A should now have ambient trust in C
        ac_edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_C
        ).first()
        assert ac_edge is not None
        assert ac_edge.trust_score == pytest.approx(0.02)


# ---------------------------------------------------------------
# Trust decay
# ---------------------------------------------------------------

class TestTrustDecay:
    def test_decay_after_15_idle_ticks(self, trust_engine):
        sim = str(uuid.uuid4())
        # Create edge at tick 0
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "alliance_formed", tick=0)
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        initial_score = edge.trust_score

        # Apply decay at tick 16 (16 - 0 = 16 >= 15 idle ticks)
        trust_engine.decay_trust(sim, current_tick=16)
        edge = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        # decay_amount = 0.01 * (16 - 0 - 14) = 0.01 * 2 = 0.02
        assert edge.trust_score == pytest.approx(initial_score - 0.02)

    def test_no_decay_if_recently_active(self, trust_engine):
        sim = str(uuid.uuid4())
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "alliance_formed", tick=10)
        edge_before = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        initial_score = edge_before.trust_score

        # Decay at tick 20 (20 - 10 = 10 < 15)
        trust_engine.decay_trust(sim, current_tick=20)
        edge_after = trust_engine.session.query(AgentTrustEdge).filter_by(
            simulation_id=sim, source_agent_id=AGENT_A, target_agent_id=AGENT_B
        ).first()
        assert edge_after.trust_score == pytest.approx(initial_score)


# ---------------------------------------------------------------
# Reputation
# ---------------------------------------------------------------

class TestReputation:
    def test_reputation_zero_with_no_edges(self, trust_engine):
        sim = str(uuid.uuid4())
        rep = trust_engine.reputation(sim, "nonexistent_agent")
        assert rep == 0.0

    def test_reputation_increases_with_incoming_trust(self, trust_engine):
        sim = str(uuid.uuid4())
        # B and C trust A
        for tick in range(1, 5):
            trust_engine.apply_event(sim, AGENT_B, AGENT_A, "cooperation_success", tick=tick)
            trust_engine.apply_event(sim, AGENT_C, AGENT_A, "cooperation_success", tick=tick)
        rep = trust_engine.reputation(sim, AGENT_A)
        assert rep > 0.0


# ---------------------------------------------------------------
# Influence
# ---------------------------------------------------------------

class TestInfluence:
    def test_influence_zero_with_no_edges(self, trust_engine):
        sim = str(uuid.uuid4())
        inf = trust_engine.influence(sim, "no_such_agent")
        assert inf == 0.0

    def test_influence_increases_with_outgoing_trust(self, trust_engine):
        sim = str(uuid.uuid4())
        # A trusts B and C
        for tick in range(1, 5):
            trust_engine.apply_event(sim, AGENT_A, AGENT_B, "cooperation_success", tick=tick)
            trust_engine.apply_event(sim, AGENT_A, AGENT_C, "cooperation_success", tick=tick)
        inf = trust_engine.influence(sim, AGENT_A)
        assert inf > 0.0


# ---------------------------------------------------------------
# get_all_edges
# ---------------------------------------------------------------

class TestGetAllEdges:
    def test_returns_edges_for_simulation(self, trust_engine):
        sim = str(uuid.uuid4())
        trust_engine.apply_event(sim, AGENT_A, AGENT_B, "cooperation_success", tick=1)
        trust_engine.apply_event(sim, AGENT_B, AGENT_C, "message_accepted", tick=2)
        edges = trust_engine.get_all_edges(sim)
        assert len(edges) == 2

    def test_does_not_return_other_simulation_edges(self, trust_engine):
        sim1 = str(uuid.uuid4())
        sim2 = str(uuid.uuid4())
        trust_engine.apply_event(sim1, AGENT_A, AGENT_B, "cooperation_success", tick=1)
        trust_engine.apply_event(sim2, AGENT_A, AGENT_C, "cooperation_success", tick=1)
        edges_sim1 = trust_engine.get_all_edges(sim1)
        assert len(edges_sim1) == 1
        assert edges_sim1[0].target_agent_id == AGENT_B
