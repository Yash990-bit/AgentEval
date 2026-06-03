# backend/app/utils/redis_pub.py
"""Utility wrapper for publishing SimulationEvent messages to Redis pub/sub.

The event payload follows the schema:
```
{
    "run_id": "<UUID>",
    "agent_id": "<UUID>",  # optional for global events
    "event_type": "<str>",
    "details": { ... }       # free‑form JSON payload
}
```
The wrapper serialises the dict to JSON and publishes to the channel
``simulation_events``.
"""

import json
from typing import Any, Dict, Optional

import redis.asyncio as redis
from pydantic import BaseModel, Field

# The Redis URL is expected via environment variable REDIS_URL
# (e.g., "redis://redis:6379/0")
REDIS_URL = "redis://redis:6379/0"

_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Lazily create a singleton async Redis client."""
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True)
    return _client


class SimulationEvent(BaseModel):
    run_id: str = Field(..., description="UUID of the simulation run")
    agent_id: Optional[str] = Field(None, description="UUID of the agent (if applicable)")
    event_type: str = Field(..., description="Type of event (think, plan, sleep, etc.)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional payload")

    class Config:
        json_encoders = {"uuid.UUID": str}


async def publish_event(event: SimulationEvent) -> None:
    """Publish a SimulationEvent to the ``simulation_events`` channel.

    The function is fire‑and‑forget – any failure to publish will be logged but
    will not raise to the caller, ensuring the simulation tick continues.
    """
    client = await get_redis_client()
    payload = event.json()
    await client.publish("simulation_events", payload)
