import pytest
import uuid
from fastapi.testclient import TestClient

from app.main import app
from app.db.models import Base
from app.db.session import SessionLocal, engine
from app.dependencies import get_s3_client

# Mock S3 Client to avoid connecting to a local minio/S3 instance during tests
class MockS3Client:
    def upload_snapshot(self, key: str, data: bytes) -> None:
        pass

app.dependency_overrides[get_s3_client] = lambda: MockS3Client()

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_analytics_endpoints():
    # 1. Start a simulation
    agent_id_1 = str(uuid.uuid4())
    agent_id_2 = str(uuid.uuid4())
    
    start_payload = {
        "agents": [
            {
                "id": agent_id_1,
                "name": "Test Agent 1",
                "role": "planner",
                "objective": "Plan out things",
                "tools": [],
                "resource_budget": 100.0,
                "trust_score": 0.8,
                "energy_score": 90.0,
                "risk_score": 0.3
            },
            {
                "id": agent_id_2,
                "name": "Test Agent 2",
                "role": "executor",
                "objective": "Execute things",
                "tools": [],
                "resource_budget": 100.0,
                "trust_score": 0.9,
                "energy_score": 95.0,
                "risk_score": 0.2
            }
        ]
    }
    
    # Start simulation
    response = client.post("/api/v1/simulation/start", json=start_payload)
    assert response.status_code == 200
    res_data = response.json()
    sim_id = res_data["simulation_id"]
    assert sim_id is not None
    
    # 2. Get simulation state to make sure it runs
    response = client.get("/api/v1/simulation/state")
    assert response.status_code == 200
    
    # Connect to websocket before stepping so we are subscribed
    with client.websocket_connect(f"/api/v1/simulations/{sim_id}/live") as websocket:
        # Step simulation (this should trigger analytics compute and broadcast)
        step_response = client.post("/api/v1/simulation/step")
        assert step_response.status_code == 200
        
        # Verify websocket broadcast
        broadcast_data = websocket.receive_json()
        assert broadcast_data["simulation_id"] == sim_id
        assert broadcast_data["total_agents"] == 2
        
    # 3. Compute analytics manually for simulation (should create DB entries)
    compute_response = client.post(f"/api/v1/simulations/{sim_id}/analytics/compute")
    assert compute_response.status_code == 200
    analytics_data = compute_response.json()
    assert analytics_data["simulation_id"] == sim_id
    assert analytics_data["total_agents"] == 2
    
    # 4. Retrieve stored analytics
    get_response = client.get(f"/api/v1/simulations/{sim_id}/analytics")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["simulation_id"] == sim_id
    assert get_data["total_agents"] == 2
    
    # 5. Retrieve agent performance metrics
    metrics_response = client.get(f"/api/v1/simulations/{sim_id}/agents/metrics")
    assert metrics_response.status_code == 200
    metrics_data = metrics_response.json()
    assert len(metrics_data) == 2
    assert any(m["agent_id"] == agent_id_1 for m in metrics_data)
    assert any(m["agent_id"] == agent_id_2 for m in metrics_data)

def test_analytics_not_found():
    # Query non-existent simulation analytics
    fake_sim_id = uuid.uuid4()
    response = client.get(f"/api/v1/simulations/{fake_sim_id}/analytics")
    assert response.status_code == 404
