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
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with correct permissions
RUN mkdir -p /app/keys/ssh /app/keys/rsa /app/keys/gpg \
    && chmod 700 /app/keys/ssh /app/keys/rsa /app/keys/gpg

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "app.py"]
