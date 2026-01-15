"""Email-related background tasks."""
import logging

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
)
def send_email_task(
    self: celery_app.Task,  # type: ignore[name-defined]
    to_email: str,
    subject: str,
    body: str,
) -> dict[str, str]:
    """
    Send an email asynchronously.

    This is a placeholder that simulates email sending.
    In production, integrate with an email service (SendGrid, SES, etc.)
    """
    logger.info(f"Sending email to {to_email}: {subject}")

    # Simulate email sending
    # In production, replace with actual email service integration
    # Example with SendGrid:
    # import sendgrid
    # sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    # ...

    logger.info(f"Email sent successfully to {to_email}")

    return {
        "status": "sent",
        "to": to_email,
        "subject": subject,
    }


@celery_app.task(bind=True)
def send_welcome_email(self: celery_app.Task, user_email: str, user_name: str) -> dict[str, str]:  # type: ignore[name-defined]
    """Send a welcome email to a new user."""
    subject = "Welcome to FastAPI App!"
    body = f"Hello {user_name},\n\nWelcome to our application!"

    return send_email_task(user_email, subject, body)


@celery_app.task(bind=True)
def send_password_reset_email(self: celery_app.Task, user_email: str, reset_token: str) -> dict[str, str]:  # type: ignore[name-defined]
    """Send a password reset email."""
    subject = "Password Reset Request"
    body = f"Click the link to reset your password: /reset?token={reset_token}"

    return send_email_task(user_email, subject, body)
