"""Health check tasks."""
import logging
from datetime import datetime

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def celery_health_check() -> dict[str, str]:
    """
    Celery health check task.

    Runs periodically to verify Celery workers are healthy.
    """
    logger.info("Celery health check: OK")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "worker": "celery",
    }
