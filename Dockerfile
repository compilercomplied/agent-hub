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


FROM base AS builder

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /app
COPY pyproject.toml README.md ./
COPY uv.lock* ./

# Create virtual environment and install dependencies
RUN /root/.local/bin/uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    /root/.local/bin/uv pip install .


FROM base AS runtime

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Set environment to use virtual environment
ENV PATH="/opt/venv/bin:$PATH"

USER appuser
WORKDIR /app
COPY --chown=appuser:appuser src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
