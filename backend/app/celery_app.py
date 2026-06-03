import os
from celery import Celery

# Celery configuration – broker and backend use Redis (env vars or defaults)
BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BACKEND_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("conflict_engine", broker=BROKER_URL, backend=BACKEND_URL)

# Optional: load config from a separate module if needed
# celery_app.config_from_object("app.celery_config")

# Autodiscover tasks in the project (conflict package includes tasks)
celery_app.autodiscover_tasks(["backend.app.conflict"])
