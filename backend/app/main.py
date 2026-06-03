from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import health, agents, simulation, relationships, conflicts

app = FastAPI(title="AI Agent Behaviour Simulator", version="0.1.0")

# Wire the global SocketManager to the FastAPI app so that InteractionEngine can emit events.
from .socket import socket_manager  # relative import from backend/app/socket.py
socket_manager.app = app

# CORS configuration (allow all for dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(agents.router, prefix="/api/v1", tags=["agents"])
app.include_router(simulation.router, prefix="/api/v1", tags=["simulation"])
app.include_router(relationships.router, prefix="/api/v1", tags=["relationships"])
app.include_router(conflicts.router, prefix="/api/v1", tags=["conflicts"])

@app.get("/api/v1/ping")
async def ping():
    return {"msg": "pong"}
