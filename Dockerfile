# Multi-stage build for optimized production image
# Stage 1: Build stage
FROM python:3.12-slim as builder

# Set environment variables for build stage
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.12-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user with specific UID/GID for security
RUN groupadd -r -g 1001 appgroup && \
    useradd -r -g appgroup -u 1001 -m -d /app -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy application code with proper ownership
COPY --chown=appuser:appgroup app/ ./app/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup scripts/ ./scripts/
COPY --chown=appuser:appgroup alembic.ini ./

# Switch to non-root user
USER appuser

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs && \
    chmod 755 /app/logs && \
    chmod +x /app/scripts/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Add security labels
LABEL maintainer="todo-api-backend" \
      version="1.0" \
      description="FastAPI Todo Backend Application" \
      security.non-root="true"

# Health check with improved configuration
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint to run migrations before starting the app
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]

# Run the application with security-focused settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--access-log"]