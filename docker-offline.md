# Running Key Generator in Podman Offline

This guide explains how to build and run the Key Generator application using Docker/Podman in an offline environment.

## Prerequisites

- Docker (for building the image)
- Podman (for running the container offline)
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

## Step 3: Load and Run with Podman (On Offline AMD64 Machine)

1. Load the image into Podman:
```bash
podman load -i key-generator.tar
```

2. Run the container:
```bash
podman run -d \
  --name key-generator \
  -p 5000:5000 \
  -v key-generator-data:/app/keys \
  key-generator:latest
```

The application will be available at `http://localhost:5000`

## Container Management Commands

- Stop the container:
```bash
podman stop key-generator
```

- Start an existing container:
```bash
podman start key-generator
```

- Remove the container:
```bash
podman rm key-generator
```

- View container logs:
```bash
podman logs key-generator
```

## Volume Management

The container uses a named volume `key-generator-data` to persist generated keys. This volume is automatically created when you first run the container.

- List volumes:
```bash
podman volume ls
```

- Inspect volume:
```bash
podman volume inspect key-generator-data
```

- Remove volume (warning: this will delete all generated keys):
```bash
podman volume rm key-generator-data
```

## Security Notes

1. The container runs with minimal privileges
2. Key storage is isolated in a dedicated volume
3. All key directories have proper permissions (700)
4. The application runs in production mode

## Troubleshooting

1. If the container fails to start, check logs:
```bash
podman logs key-generator
```

2. If you need to access the container shell:
```bash
podman exec -it key-generator /bin/bash
```

3. If port 5000 is already in use, change the port mapping (e.g., `-p 8080:5000`)
