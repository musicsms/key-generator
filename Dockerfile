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
    openssl-dev

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Final stage
FROM python:3.13-alpine

# Install runtime dependencies
RUN apk add --no-cache \
    gnupg \
    openssh-client

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/keys/{ssh,rsa,pgp} && \
    mkdir -p /app/keys/.gnupg && \
    chmod 700 /app/keys/.gnupg

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    KEY_STORAGE_PATH=/app/keys \
    GNUPGHOME=/app/keys/.gnupg

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
