# Developer Operations Manual

This guide describes how to run local development tasks, write automated unit tests, and extend the features of the **AI Agent Behavior Simulator (AABS)**.

---

## 1. Local Development Setup

To run the frontend and backend servers locally outside of Docker:

### A. Backend Development (FastAPI)
1. **Initialize Virtual Environment**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
2. **Launch API Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *Swagger docs will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

### B. Frontend Development (Next.js)
1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```
2. **Launch dev client**:
   ```bash
   npm run dev
   ```
   *The hot-reloaded dev client will start on [http://localhost:3000](http://localhost:3000).*

---

## 2. Executing Tests

* **Run Backend Unit Tests (Pytest)**:
   ```bash
   cd backend
   pytest --cov=app tests/
   ```
* **Run Frontend Linter & Build verification**:
   ```bash
   cd frontend
   npm run lint
   npm run build
   ```

---

## 3. Adding New Agent Actions

Agent behavioral choices are governed by their roles, objectives, and internal states (defined in `backend/app/models/agent.py` and `backend/app/core/engine.py`).

To add a new action:
1. **Define the Action Model**:
   Open [backend/app/models/agent.py](file:///Users/yashraghubanshi/Desktop/AI-Agent%20Behaviour%20Simulator/backend/app/models/agent.py) or `backend/app/schemas/agent.py` and add properties if required.
2. **Update the Engine logic**:
   Open [backend/app/core/engine.py](file:///Users/yashraghubanshi/Desktop/AI-Agent%20Behaviour%20Simulator/backend/app/core/engine.py). Modify `_apply_resources` or add a new core handler method:
   ```python
   def _perform_agent_collaboration(self, agent: AgentSchema) -> AgentSchema:
       # Custom resource adjustment or goal progress evaluation logic
       agent.energy_score = min(100, agent.energy_score + 10)
       return agent
   ```
3. **Register Action in Loop**:
   Call this method in the `run_tick` method inside `engine.py`.

---

## 4. Creating New Simulation Events

Environmental dynamics (hazards, events) are governed by the Environment class in `backend/app/core/environment.py`.

To add a custom event handler:
1. **Add Event Constant**:
   Define the event string in `backend/app/core/environment.py` (e.g. `API_CRASH_WARNING`).
2. **Implement Trigger Conditions**:
   Modify `advance()` inside the `Environment` class to specify when the event triggers (e.g. if ticks exceed a threshold, or if budget falls below a specific limit):
   ```python
   if self.tick_counter > 50 and random.random() < 0.05:
       # Trigger custom event
       self.trigger_event("API_CRASH_WARNING", severity="critical")
   ```
3. **Handle Event in Engine**:
   In [engine.py](file:///Users/yashraghubanshi/Desktop/AI-Agent%20Behaviour%20Simulator/backend/app/core/engine.py), add logic to handle the event when active:
   ```python
   if self.env.is_event_active("API_CRASH_WARNING"):
       for agent in self.agents:
           # Double the API call consumption rate under failure
           agent.api_calls_count += 2
   ```
