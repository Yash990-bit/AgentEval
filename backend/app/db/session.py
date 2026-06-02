# backend/app/db/session.py
"""SQLAlchemy session helper.
Environment variable ``DATABASE_URL`` is expected (e.g. ``postgresql+psycopg2://user:pass@db:5432/simulator``).
If the variable is missing, we fall back to an in‑memory SQLite DB for development.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)

# Scoped session for thread‑local usage (FastAPI will depend on it)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    """FastAPI dependency that yields a DB session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
