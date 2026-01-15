"""Celery application configuration."""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "fastapi_app",
    broker=str(settings.CELERY_BROKER_URL),
    backend=str(settings.CELERY_RESULT_BACKEND),
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Result settings
    result_expires=3600,  # 1 hour
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

# Celery Beat schedule (scheduled tasks)
celery_app.conf.beat_schedule = {
    "cleanup-expired-tokens-every-hour": {
        "task": "app.tasks.cleanup.cleanup_expired_tokens",
        "schedule": 3600.0,  # Every hour
    },
    "health-check-every-5-minutes": {
        "task": "app.tasks.health.celery_health_check",
        "schedule": 300.0,  # Every 5 minutes
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks.email", "app.tasks.cleanup", "app.tasks.health"])
