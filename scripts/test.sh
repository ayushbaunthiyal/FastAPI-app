#!/usr/bin/env bash

set -e
set -x

# Run linting
uv run ruff check .
uv run ruff format --check .
uv run mypy .

# Run tests
uv run pytest --cov=app --cov-report=term-missing tests "${@}"
