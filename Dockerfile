# Build stage
FROM python:3.13-alpine AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    cargo

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Final stage
FROM python:3.13-alpine

# Create non-root user
RUN adduser -D appuser

# Install runtime dependencies
RUN apk add --no-cache \
    gnupg \
    openssh-client \
    curl \
    && mkdir -p /app/keys \
    && chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy application code
COPY --chown=appuser:appuser . .

# Set proper permissions for keys directory and gnupg home
RUN mkdir -p /home/appuser/.gnupg && \
    chmod 700 /home/appuser/.gnupg && \
    chown -R appuser:appuser /home/appuser/.gnupg /app/keys && \
    chmod -R 700 /app/keys

# Set environment variables
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=5001 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GNUPGHOME=/home/appuser/.gnupg

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--threads", "2", "--timeout", "60", "app:app"]
