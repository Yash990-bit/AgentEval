import pytest
from datetime import datetime

from backend.app.graph.agent_graph import (
    execute_action,
    ACTION_MAP,
    think,
    plan,
    communicate,
    use_tool,
    negotiate,
    cooperate,
    compete,
    sleep,
    escalate,
    fail,
)


@pytest.fixture
def base_state():
    return {
        "agent_id": "test-agent",
        "memory_short_term": [],
        "memory_long_term": [],
        "current_plan": [],
        "current_action": None,
        "messages_outbox": [],
        "messages_inbox": [],
        "tools_called": [],
        "resource_budget": {"compute_units": 10, "api_calls": 5, "tokens": 1000, "usd_budget": 10.0},
        "energy_score": 1.0,
        "status": "idle",
    }

def test_think_adds_thought(base_state):
    new_state = think(base_state, "sample input")
    assert len(new_state["memory_short_term"]) == 1
    thought = new_state["memory_short_term"][0]
    assert thought["content"] == "sample input"

def test_plan_creates_plan(base_state):
    goal = "achieve something"
    new_state = plan(base_state, goal)
    assert new_state["current_plan"] == ["think", "communicate", "use_tool", "sleep"]
    assert new_state["objective"] == goal

def test_communicate_adds_message(base_state):
    msg = "hello agents"
    new_state = communicate(base_state, msg)
    assert len(new_state["messages_outbox"]) == 1
    assert new_state["messages_outbox"][0]["content"] == msg

def test_use_tool_decrements_api_calls(base_state):
    new_state = use_tool(base_state, "tool-1", {"param": 1})
    assert new_state["resource_budget"]["api_calls"] == base_state["resource_budget"]["api_calls"] - 1
    assert len(new_state["tools_called"]) == 1
    assert new_state["tools_called"][0]["tool_id"] == "tool-1"

def test_negotiate_adds_to_inbox(base_state):
    proposal = {"action": "share", "value": 5}
    new_state = negotiate(base_state, proposal)
    assert len(new_state["messages_inbox"]) == 1
    assert new_state["messages_inbox"][0]["proposal"] == proposal

def test_cooperate_increases_energy(base_state):
    new_state = cooperate(base_state, "partner-1", 10)
    # energy should increase but cap at 1.0
    assert new_state["energy_score"] == 1.0

def test_compete_decreases_energy(base_state):
    state = {**base_state, "energy_score": 0.5}
    new_state = compete(state, "opponent-1", 20)
    expected = max(0.0, 0.5 - 20 * 0.01)
    assert new_state["energy_score"] == expected

def test_sleep_restores_energy_and_status(base_state):
    state = {**base_state, "energy_score": 0.4, "status": "idle"}
    new_state = sleep(state)
    assert new_state["energy_score"] == min(1.0, 0.4 + 0.05)
    assert new_state["status"] == "sleeping"

def test_escalate_sets_failed_status(base_state):
    new_state = escalate(base_state, "critical issue")
    assert new_state["status"] == "failed"

def test_fail_records_reason(base_state):
    reason = "unrecoverable error"
    new_state = fail(base_state, reason)
    assert new_state["status"] == "failed"
    assert new_state["failure_reason"] == reason

# Verify dynamic dispatch works for all actions
@pytest.mark.parametrize("action_name, args, kwargs, expected_key", [
    ("think", ("data",), {}, "memory_short_term"),
    ("plan", ("goal",), {}, "current_plan"),
    ("communicate", ("msg",), {}, "messages_outbox"),
    ("use_tool", ("tool", {"p":1}), {}, "tools_called"),
    ("negotiate", ({"prop":2},), {}, "messages_inbox"),
    ("cooperate", ("partner", 5), {}, "energy_score"),
    ("compete", ("opp", 5), {}, "energy_score"),
    ("sleep", (), {}, "status"),
    ("escalate", ("issue",), {}, "status"),
    ("fail", ("reason",), {}, "failure_reason"),
])
def test_execute_action(action_name, args, kwargs, expected_key, base_state):
    new_state = execute_action(base_state, action_name, *args, **kwargs)
    assert expected_key in new_state
