# syntax=docker/dockerfile:1
# =============================================================================
# Multi-Role 12-Factor Container Blueprint for Cresmo Modular Monolith
# Governed by: ADR-005 & SPEC-006
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Astral UV Binary Provider
# -----------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:latest AS uv-bin

# -----------------------------------------------------------------------------
# Stage 2: Final Runtime Image
# -----------------------------------------------------------------------------
FROM python:3.13-slim-bookworm AS runtime

# System runtime dependencies (ffmpeg for media extraction, curl for healthchecks)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        ca-certificates \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Copy uv binaries into system PATH
COPY --from=uv-bin /uv /uvx /bin/

# Configure Python and uv execution environment
ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Create unprivileged system user for 12-Factor least privilege security
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -s /bin/sh appuser && \
    mkdir -p /app/data /app/vault && \
    chown -R appuser:appgroup /app/data /app/vault

# Cache dependencies first (Layer caching optimization)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy application source code and entrypoint
COPY src/ ./src/
COPY docker/ ./docker/
RUN chmod +x docker/entrypoint.sh

# Install application project package into virtualenv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev && \
    chown -R appuser:appgroup /app/data /app/vault

# Drop privileges to non-root user
USER appuser

# Expose decoupled storage mount volumes
VOLUME ["/app/data", "/app/vault"]

# Routing entrypoint
ENTRYPOINT ["/app/docker/entrypoint.sh"]

# Default role execution
CMD ["check-config"]
