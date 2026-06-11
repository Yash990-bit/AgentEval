# backend/tests/test_predictions.py
import pytest
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.db.models import Base
from app.db.session import SessionLocal, engine
from app.services.prediction_engine import PredictionEngine

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Ensure prediction models are trained and saved
    PredictionEngine.train_and_save_models()
    yield
    Base.metadata.drop_all(bind=engine)

def test_prediction_endpoints():
    simulation_id = str(uuid.uuid4())

    # 1. Test Resource Exhaustion forecast
    response = client.get(f"/api/v1/predictions/{simulation_id}/resource_exhaustion")
    assert response.status_code == 200
    res_data = response.json()
    assert isinstance(res_data, list)
    assert len(res_data) > 0
    assert "resource_type" in res_data[0]
    assert "predicted_exhaustion_tick" in res_data[0]

    # 2. Test Conflict Probability forecast
    response = client.get(f"/api/v1/predictions/{simulation_id}/conflict_probability")
    assert response.status_code == 200
    conf_data = response.json()
    assert isinstance(conf_data, list)
    assert len(conf_data) > 0
    assert "agent_pair" in conf_data[0]
    assert "conflict_probability" in conf_data[0]

    # 3. Test Goal Completion forecast
    response = client.get(f"/api/v1/predictions/{simulation_id}/goal_completion")
    assert response.status_code == 200
    goal_data = response.json()
    assert "goal_id" in goal_data
    assert "completion_probability" in goal_data
    assert "expected_completion_tick" in goal_data

    # 4. Test Agent Failure Risk forecast
    response = client.get(f"/api/v1/predictions/{simulation_id}/agent_failure_risk")
    assert response.status_code == 200
    fail_data = response.json()
    assert isinstance(fail_data, list)
    assert len(fail_data) > 0
    assert "agent_id" in fail_data[0]
    assert "failure_probability" in fail_data[0]
