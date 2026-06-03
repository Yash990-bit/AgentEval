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
