# backend/app/utils/redis_pub.py
"""Utility stub for publishing simulation events.
In the test environment we don't need actual Redis publishing, so this
function is a no-op placeholder that matches the original call signature
used throughout the codebase.
"""

def publish_event(event_type: str, details: dict) -> None:
    """Placeholder for event publishing.
    Parameters
    ----------
    event_type: str
        The type of event (e.g., "thought_generated").
    details: dict
        Event payload dictionary.
    """
    # No operation – in production this would publish to Redis.
    return
