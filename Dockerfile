# Build stage
FROM --platform=linux/amd64 python:3.9-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Final stage
FROM --platform=linux/amd64 python:3.9-slim

# Create non-root user
RUN useradd -r -s /bin/false appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    openssh-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/keys \
    && chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy application code
COPY --chown=appuser:appuser . .

# Set proper permissions
RUN chmod 700 /app/keys

# Set environment variables
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=5001 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Run Gunicorn with security settings
CMD ["gunicorn", \
    "--bind", "0.0.0.0:5001", \
    "--workers", "4", \
    "--timeout", "120", \
    "--worker-class", "sync", \
    "--worker-tmp-dir", "/dev/shm", \
    "--log-level", "info", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--capture-output", \
    "--enable-stdio-inheritance", \
    "app:app"]
