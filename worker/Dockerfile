# --- Build Stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install packages
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Runtime Stage ---
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (e.g. libpq, curl/celery inspect for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from build stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create a non-root user and set permissions
RUN useradd -u 10001 -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Healthcheck for Celery worker
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD celery -A app.celery_app inspect ping || exit 1

CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info"]
