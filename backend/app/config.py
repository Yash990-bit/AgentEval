# backend/app/config.py
"""AABS backend configurations and parameters."""

# Conflict detection settings
CONFLICT_DETECTION_TICK_INTERVAL = 1
COMMUNICATION_WINDOW_TICKS = 5

# Global resource capacities for conflict checking
RESOURCE_CAPACITY = {
    "compute_units": 5,
    "api_calls": 5,
    "tokens": 1000,
    "usd_budget": 10.0,
}

import os

# Qdrant settings for Long‑Term Memory
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "agent_ltm")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

