import uuid
import random
from locust import HttpUser, task, between

class SimulationLoadTestUser(HttpUser):
    # Simulate users clicking and reviewing dashboards every 1-3 seconds
    wait_time = between(1, 3)

    def on_start(self):
        """Initialize user session and start a simulation with 200 agents."""
        self.simulation_id = None
        self.agents = [
            {
                "id": str(uuid.uuid4()),
                "name": f"Agent_{i}",
                "role": random.choice(["Coordinator", "Planner", "Researcher", "Analyst", "Security Auditor"]),
                "objective": f"Resolve simulated system sub-system priority conflict #{i}",
                "energy_score": random.randint(80, 100),
                "resource_budget": random.uniform(50.0, 100.0),
                "trust_score": random.uniform(0.6, 1.0),
                "risk_score": random.uniform(0.0, 0.3)
            }
            for i in range(200) # Sustained 200-agent load test configuration
        ]
        self.start_simulation()

    def start_simulation(self):
        """Starts a simulation run via backend endpoint."""
        payload = {"agents": self.agents}
        with self.client.post("/api/v1/simulation/start", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.simulation_id = data.get("simulation_id")
                response.success()
            else:
                response.failure(f"Failed to start simulation: {response.text}")

    @task(3)
    def step_simulation(self):
        """Simulates advancing the simulation clock by 1 tick."""
        if not self.simulation_id:
            return
        
        headers = {"X-Simulation-ID": self.simulation_id}
        with self.client.post("/api/v1/simulation/step", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Step tick failed: {response.text}")

    @task(5)
    def view_state(self):
        """Simulates frontend polling the active simulation state."""
        with self.client.get("/api/v1/simulation/state", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to read state: {response.text}")

    @task(2)
    def get_evaluations(self):
        """Simulates fetching real-time agent ranking evaluations."""
        with self.client.get("/api/v1/simulation/evaluations", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to read evaluations: {response.text}")

    @task(1)
    def trigger_failure_injection(self):
        """Injects random failures or resource scarcity to test agent response."""
        failure_payload = {
            "simulation_id": self.simulation_id,
            "failure_type": random.choice(["inject_tool_failure", "inject_hallucination", "resource_scarcity_warning"]),
            "agent_id": random.choice(self.agents)["id"]
        }
        with self.client.post("/api/v1/failures/inject", json=failure_payload, catch_response=True) as response:
            if response.status_code in [200, 201, 404]: # Allow 404 if endpoint database tables aren't pre-loaded
                response.success()
            else:
                response.failure(f"Failed to inject error: {response.text}")
