import os
from celery import Celery

# Celery configuration – broker and backend use Redis (env vars or defaults)
BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BACKEND_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("conflict_engine", broker=BROKER_URL, backend=BACKEND_URL)

# Optional: load config from a separate module
celery_app.config_from_object("backend.celeryconfig")

# Autodiscover tasks in the project (conflict and tasks packages)
celery_app.autodiscover_tasks(["backend.app.conflict", "backend.app.tasks"])
