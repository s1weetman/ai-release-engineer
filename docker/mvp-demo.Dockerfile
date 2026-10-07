FROM python:3.12-slim

WORKDIR /opt/ai-release-engineer

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --no-cache-dir ".[dev]"

WORKDIR /workspace
