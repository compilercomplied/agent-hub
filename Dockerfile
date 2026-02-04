# Multi-stage Dockerfile for Agent Hub API

# Stage 1: Base image with Python and system dependencies
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Builder stage for installing dependencies
FROM base AS builder

# Install uv for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock* ./

# Create virtual environment and install dependencies
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache fastapi uvicorn[standard] pydantic

# Stage 3: Runtime stage
FROM base AS runtime

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Set environment to use virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 4: Test stage for e2e tests
FROM runtime AS test

# Switch back to root to install test dependencies
USER root

# Install test dependencies
RUN . /opt/venv/bin/activate && \
    /opt/venv/bin/python -m pip install --no-cache-dir pytest httpx

# Switch back to appuser
USER appuser

# Copy test files
COPY --chown=appuser:appuser e2e/ ./e2e/

# Override CMD for test stage
CMD ["pytest", "e2e/", "-v", "--tb=short"]
