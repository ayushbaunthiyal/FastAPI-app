"""API benchmark tests."""
import time

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_endpoint_response_time(client: AsyncClient) -> None:
    """
    Measure response time of logic endpoint.
    
    This is a basic benchmark assertion. In a real CI, use pytest-benchmark.
    """
    start_time = time.perf_counter()
    response = await client.get("/health/live")
    duration = time.perf_counter() - start_time
    
    assert response.status_code == 200
    # Ensure health check is under 100ms
    assert duration < 0.1, f"Response too slow: {duration:.4f}s"
