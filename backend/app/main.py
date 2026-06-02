from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import health, agents, simulation

app = FastAPI(title="AI Agent Behaviour Simulator Backend", version="0.1.0")

# Allow frontend (localhost:3000) to call the API
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

@app.get("/api/v1/ping")
async def ping():
    return {"msg": "pong"}
