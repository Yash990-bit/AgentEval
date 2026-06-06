from .failures import router as failures_router
from .emergent import router as emergent_router

# Export routers for automatic inclusion elsewhere
__all__ = ["failures_router", "emergent_router"]
# Package initializer for versioned API routes
