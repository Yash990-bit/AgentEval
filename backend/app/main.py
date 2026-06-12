import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from .utils.logging_setup import setup_structured_logging, StructuredLoggingMiddleware

# Initialize Sentry
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        environment=os.getenv("ENV", "production")
    )

# Setup structured logging
setup_structured_logging()

# Import API routers
from .api.v1 import (
    health,
    agents,
    simulation,
    relationships,
    resource,
    failures as failures_module,
    emergent,
    agent_templates,
    replay,
    analytics,
    predictions,
)
from .api.v1.trust import router as trust_router
from .api.v1.conflicts import router as conflicts_router

"""FastAPI application entry point with all API routers, including predictions."""

app = FastAPI(title="AI Agent Behaviour Simulator", version="0.1.0")

# Instrument FastAPI with Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Add custom structured logging middleware
app.add_middleware(StructuredLoggingMiddleware)

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
app.include_router(conflicts_router, prefix="/api/v1", tags=["conflicts"])
app.include_router(resource.router, prefix="/api/v1", tags=["resource"])
app.include_router(failures_module.router, prefix="/api/v1", tags=["failures"])
app.include_router(emergent.router, prefix="/api/v1", tags=["emergent"])
app.include_router(trust_router, prefix="/api/v1", tags=["trust"])
app.include_router(agent_templates.router, prefix="/api/v1", tags=["agent_templates"])
app.include_router(replay.router, prefix="/api/v1", tags=["replay"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])

@app.on_event("startup")
async def start_failure_detection():
    import asyncio
    from .services.failure_engine import run_detection_cycle
    from .db.session import SessionLocal

    async def detection_loop():
        while True:
            try:
                db = SessionLocal()
                # TODO: Fetch active simulation IDs and agent states
                simulation_ids = []
                for sim_id in simulation_ids:
                    agents_state = []
                    tick = 0
                    run_detection_cycle(db, sim_id, agents_state, tick)
                db.close()
            except Exception as e:
                print(f"Failure detection error: {e}")
            await asyncio.sleep(5)

    asyncio.create_task(detection_loop())

@app.get("/api/v1/ping")
async def ping():
    return {"msg": "pong"}
