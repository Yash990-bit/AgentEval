# backend/celeryconfig.py
import os
from celery.schedules import crontab

broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
result_backend = os.getenv("REDIS_URL", "redis://localhost:6379/0")

timezone = "UTC"
accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"

beat_schedule = {
    "train-prediction-models-every-5-min": {
        "task": "train_prediction_models_task",
        "schedule": 300.0,  # 5 minutes
    },
}
