"""Root-level shim to expose the FastAPI application for tests.
This file re-exports the FastAPI instance defined in the backend package.
"""

from backend.app.main import app  # noqa: F401
