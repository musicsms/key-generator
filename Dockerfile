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
    cargo \
    libgcc \
    libstdc++

# Upgrade pip and setuptools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies with additional security checks
RUN pip install --no-cache-dir \
    --use-pep517 \
    --prefer-binary \
    --no-warn-script-location \
    -r requirements.txt \
    && pip check

# Verify cryptography installation
RUN pip show cryptography

# Final stage
FROM python:3.13-alpine

# Create non-root user
RUN adduser -D appuser

# Install runtime dependencies
RUN apk add --no-cache \
    gnupg \
    openssh-client \
    curl \
    ca-certificates \
    openssl \
    && update-ca-certificates \
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
    chmod -R 700 /app/keys && \
    # Remove unnecessary files and set restrictive permissions
    find /app -type f -exec chmod 640 {} \; && \
    find /app -type d -exec chmod 750 {} \;

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONWARNINGS="ignore:Unverified HTTPS request,ignore:Unverified OpenSSL" \
    GNUPGHOME=/home/appuser/.gnupg \
    PATH="/home/appuser/.local/bin:$PATH" \
    FLASK_ENV=production \
    FLASK_APP=app.py \
    CRYPTOGRAPHY_ALLOW_OPENSSL_102=1 \
    CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1 \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
    SECRET_KEY=CHANGE_ME_IN_PRODUCTION

# Expose port
EXPOSE 5001

# Run with gunicorn with additional security flags
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5001", \
     "--workers", "4", \
     "--timeout", "300", \
     "--limit-request-line", "4094", \
     "--limit-request-fields", "100", \
     "--limit-request-field-size", "8190", \
     "--worker-tmp-dir", "/dev/shm", \
     "--secure-scheme-headers", "{'X-FORWARDED-PROTO': 'https'}", \
     "app:app"]
