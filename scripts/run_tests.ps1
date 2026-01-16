# Test Runner Script
Write-Host "Starting Test Suite (Dockerized)..." -ForegroundColor Cyan

# Define the image to use
$CI_IMAGE = "ghcr.io/astral-sh/uv:python3.12-bookworm-slim"

# Run Tests
docker run --rm `
    -v "${PWD}:/app" `
    -w /app `
    -v "/app/.venv" `
    -e "ENVIRONMENT=test" `
    $CI_IMAGE `
    sh -c "uv sync --all-extras --dev && uv run pytest tests" 

if ($LASTEXITCODE -ne 0) { Write-Error "Tests failed!" } else { Write-Host "Tests Passed!" -ForegroundColor Green }
