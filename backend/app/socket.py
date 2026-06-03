import logging
from typing import Any

logger = logging.getLogger(__name__)

class SocketManager:
    """Mock/wrapper class for Socket.io or WebSocket manager."""
    def __init__(self, app=None):
        self.app = app

    async def emit(self, event: str, data: Any):
        logger.info(f"Socket emit: {event} -> {data}")

socket_manager = SocketManager()
