# Use AMD64 base image explicitly
FROM --platform=linux/amd64 python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gnupg \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Create directory for keys
RUN mkdir -p /app/keys && chmod 700 /app/keys

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5001

# Expose port
EXPOSE 5001

# Run Gunicorn with 4 worker processes
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "4", "--timeout", "120", "app:app"]
