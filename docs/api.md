# API Reference Manual

Welcome to the AI Agent Behavior Simulator (AABS) API manual. The AABS backend exposes REST endpoints for configuring, stepping, and analyzing agent simulation runs.

## 1. Authentication Guide

All production API requests must include a valid bearer token in the `Authorization` header:

```http
Authorization: Bearer <your_api_token>
```

Tokens are generated and managed within the Enterprise Admin console. 
In local development environments (`ENV=development`), authentication verification is bypassed.

---

## 2. Rate Limits

Production endpoints enforce rate limits based on client IP addresses and organizations:
* **Staging/Sandbox**: 60 requests per minute per IP.
* **Production/Enterprise**: 1200 requests per minute per organization token.

Exceeding these thresholds triggers an HTTP `429 Too Many Requests` response:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 24 seconds."
}
```

---

## 3. Core Endpoint Specifications

### A. Start Simulation
Initializes the simulation engine.

* **URL**: `/api/v1/simulation/start`
* **Method**: `POST`
* **Payload**:
```json
{
  "agents": [
    {
      "id": "agent-uuid-1",
      "name": "ARIA-7",
      "role": "Coordinator",
      "energy_score": 100,
      "resource_budget": 80.0,
      "trust_score": 0.9,
      "risk_score": 0.05
    }
  ]
}
```
* **Response (200 OK)**:
```json
{
  "status": "started",
  "agent_count": 1,
  "simulation_id": "c623910c-982c-473d-82d3-1a28a3f89012"
}
```

### B. Step Simulation
Advances the simulation clock by 1 tick, records DB state, and returns the step snapshot.

* **URL**: `/api/v1/simulation/step`
* **Method**: `POST`
* **Response (200 OK)**:
```json
{
  "agents": [
    {
      "id": "agent-uuid-1",
      "name": "ARIA-7",
      "role": "Coordinator",
      "energy_score": 87.0,
      "resource_budget": 78.4,
      "trust_score": 0.89,
      "risk_score": 0.06,
      "status": "active"
    }
  ],
  "links": [],
  "time": "2026-06-12T10:00:01Z",
  "resources": {
    "compute_units": 5,
    "api_calls": 5,
    "tokens": 1000,
    "usd_budget": 10.0
  },
  "events": [],
  "hazards": []
}
```

### C. Get Evaluations
Retrieves rank-ordered evaluations of the active swarm.

* **URL**: `/api/v1/simulation/evaluations`
* **Method**: `GET`
* **Response (200 OK)**:
```json
{
  "agents": [
    {
      "id": "agent-uuid-1",
      "name": "ARIA-7",
      "intelligence": 90.0,
      "cooperation": 85.0,
      "reliability": 95.0,
      "efficiency": 88.0,
      "risk": 15.0,
      "composite": 88.55,
      "rank": 1
    }
  ],
  "summary": {
    "avg_intelligence": 90.0,
    "avg_cooperation": 85.0,
    "avg_reliability": 95.0,
    "avg_efficiency": 88.0,
    "avg_risk": 15.0,
    "avg_composite": 88.55
  }
}
```

---

## 4. Webhook Events

AABS can push real-time event logs to configured webhook listeners. Register endpoints in `Settings`.

### Event: `simulation.conflict_detected`
Fired when the engine detects a goal deadlock or coordination breakdown.

```json
{
  "event_id": "evt_9a82b3d8",
  "event_type": "simulation.conflict_detected",
  "timestamp": "2026-06-12T15:30:12Z",
  "data": {
    "simulation_id": "c623910c-982c-473d-82d3-1a28a3f89012",
    "conflict_id": "conf-749",
    "severity": "critical",
    "description": "Resource Lock Deadlock between ARIA-7 and ECHO-1"
  }
}
```
