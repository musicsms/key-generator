# Running Key Generator in Docker Offline

This guide explains how to build and run the Key Generator application using Docker in an offline environment.

## Prerequisites

- Docker (for building and running the container)
- Internet connection (only for initial build)
- QEMU for cross-platform builds (if building on ARM64 for AMD64)

## Step 1: Prepare Build Environment (On ARM64 Machine with Internet)

1. Install QEMU and enable multi-architecture support:
```bash
docker run --privileged --rm tonistiigi/binfmt --install all
```

2. Navigate to the project directory:
```bash
cd key-generator
```

3. Build the Docker image for AMD64:
```bash
docker buildx create --use
docker buildx build --platform linux/amd64 -t key-generator:latest --load .
```

4. Save the image to a tar file:
```bash
docker save -o key-generator.tar key-generator:latest
```

## Step 2: Transfer the Image (To Offline Machine)

Transfer the `key-generator.tar` file to the offline machine using any available method (USB drive, network transfer, etc.).

## Step 3: Load and Run with Docker (On Offline AMD64 Machine)

1. Load the image into Docker:
```bash
docker load -i key-generator.tar
```

2. Run the container:
```bash
docker run -d \
  --name key-generator \
  -p 5001:5001 \
  -v ./keys:/app/keys \
  key-generator:latest
```

The application will be available at `http://localhost:5001`

## Container Management Commands

- Stop the container:
```bash
docker stop key-generator
```

- Start an existing container:
```bash
docker start key-generator
```

- Remove the container:
```bash
docker rm key-generator
```

- View container logs:
```bash
docker logs key-generator
```

## Volume Management

The container uses a local volume `./keys` to persist generated keys. This directory will be created automatically when you first run the container.

- List volumes:
```bash
docker volume ls
```

- Inspect volume:
```bash
docker volume inspect key-generator
```

- Remove volume (warning: this will delete all generated keys):
```bash
rm -rf ./keys
```

## Security Notes

1. The container runs with minimal privileges
2. Key storage is isolated in a dedicated volume
3. All connections are made through port 5001
4. The application runs with production-grade Gunicorn server

## Using Docker Compose

You can also use Docker Compose for easier management:

1. Start the application:
```bash
docker-compose up -d
```

2. Stop the application:
```bash
docker-compose down
```

3. View logs:
```bash
docker-compose logs -f
```
