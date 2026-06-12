import logging
import json
import time
import uuid
import os
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "levelname": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "filename": record.filename,
            "lineno": record.lineno,
        }
        
        # Safely copy dynamic telemetry labels
        for field in ["trace_id", "org_id", "user_id", "simulation_id", "duration_ms", "status_code"]:
            if hasattr(record, field):
                val = getattr(record, field)
                if val is not None:
                    log_data[field] = val
                    
        return json.dumps(log_data)

def setup_structured_logging():
    env_name = os.getenv("ENV", "production").lower()
    
    # DEBUG in local, INFO in staging, WARNING+ in production
    if env_name == "local" or env_name == "development":
        log_level = logging.DEBUG
    elif env_name == "staging":
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    # Remove existing default handlers
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
        
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Suppress verbose dependency logs in production
    if log_level >= logging.WARNING:
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("fastapi").setLevel(logging.WARNING)

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Read or generate transaction tracing tags
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        org_id = request.headers.get("X-Org-ID", "org-agentverse-enterprise")
        user_id = request.headers.get("X-User-ID", "user-yash")
        
        # Resolve simulation ID context if query contains it
        simulation_id = request.query_params.get("simulation_id") or request.headers.get("X-Simulation-ID")

        request.state.trace_id = trace_id
        request.state.org_id = org_id
        request.state.user_id = user_id
        request.state.simulation_id = simulation_id

        try:
            response: Response = await call_next(request)
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger = logging.getLogger("aabs.request")
            logger.error(
                f"Unhandled exception during request processing: {str(e)}",
                extra={
                    "trace_id": trace_id,
                    "org_id": org_id,
                    "user_id": user_id,
                    "simulation_id": simulation_id,
                    "duration_ms": duration_ms,
                    "status_code": 500
                }
            )
            raise e
        
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        # Log request summary to stdout as structured JSON
        logger = logging.getLogger("aabs.request")
        logger.warning(
            f"{request.method} {request.url.path} resolved with status {response.status_code} in {duration_ms}ms",
            extra={
                "trace_id": trace_id,
                "org_id": org_id,
                "user_id": user_id,
                "simulation_id": simulation_id,
                "duration_ms": duration_ms,
                "status_code": response.status_code
            }
        )
        
        response.headers["X-Trace-ID"] = trace_id
        return response
