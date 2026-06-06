'''Service package initializer
Provides a convenient factory for the TrustEngine.
'''

from sqlalchemy.orm import Session

from .trust_engine import TrustEngine

def get_trust_engine(db: Session) -> TrustEngine:
    """Return a TrustEngine bound to the supplied SQLAlchemy session.

    The function is lightweight – it simply wraps the session in a TrustEngine
    instance.  It is imported by the Trust API router (``api/v1/trust.py``) so
    that each request gets a fresh engine tied to the request‑scoped session.
    """
    return TrustEngine(db)

__all__ = ["get_trust_engine", "TrustEngine"]
