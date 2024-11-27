# Build stage
FROM python:3.9-slim AS builder

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
FROM python:3.9-slim

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

# Set proper permissions for keys directory and gnupg home
RUN mkdir -p /root/.gnupg && \
    chmod 700 /root/.gnupg && \
    chown -R appuser:appuser /app/keys && \
    chmod -R 700 /app/keys

# Set environment variables
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=5001 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GNUPGHOME=/root/.gnupg

# Switch to non-root user for running the application
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--threads", "2", "--timeout", "60", "app:app"]
