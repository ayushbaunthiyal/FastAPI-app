"""Integration tests for background tasks."""
import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_trigger_email_task_unauthorized(client: AsyncClient) -> None:
    """Test triggering task without auth (should fail if auth protected)."""
    # Currently tasks endpoint is open, need to verify
    response = await client.post(
        f"{settings.API_V1_STR}/tasks/trigger/email",
        json={"to_email": "test@example.com", "subject": "Test", "body": "Body"},
    )
    # If we add auth later, this should be 401
    # For now it's 200 or 404 depending on implementation
    assert response.status_code in [200, 202]
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"
