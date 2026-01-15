"""Task management endpoints."""
from typing import Any

from fastapi import APIRouter

from app.tasks.email import send_email_task
from app.tasks.cleanup import cleanup_expired_tokens

router = APIRouter()


@router.post("/trigger/email")
async def trigger_email_task(
    to_email: str = "test@example.com",
    subject: str = "Test Email",
    body: str = "This is a test email from the background task.",
) -> dict[str, Any]:
    """
    Trigger a test email task.

    This endpoint queues an email task for background processing.
    """
    task = send_email_task.delay(to_email, subject, body)
    return {
        "message": "Email task queued",
        "task_id": task.id,
        "status": "pending",
    }


@router.post("/trigger/cleanup")
async def trigger_cleanup_task() -> dict[str, Any]:
    """
    Trigger cleanup task manually.

    This task normally runs on a schedule but can be triggered manually.
    """
    task = cleanup_expired_tokens.delay()
    return {
        "message": "Cleanup task queued",
        "task_id": task.id,
        "status": "pending",
    }


@router.get("/status/{task_id}")
async def get_task_status(task_id: str) -> dict[str, Any]:
    """
    Get the status of a background task.
    """
    from app.core.celery_app import celery_app

    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
