# Offline Docker Deployment Guide for Key Generator

## Prerequisites

- Docker (version 20.10 or higher)
- Offline Docker image tarball
- Linux/macOS/Windows with Docker support

## Offline Installation Steps

### 1. Load Docker Image

```bash
# Load the image from the tarball
docker load -i key-generator.tar
```

### 2. Verify Image

```bash
# Confirm the image is loaded
docker images | grep key-generator
```

### 3. Run Offline Container

```bash
# Basic run command
docker run -d \
  --name key-generator \
  -p 5001:5001 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secure-secret-key \
  -v key-storage:/app/keys \
  -v gpg-home:/home/appuser/.gnupg \
  key-generator:latest
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| FLASK_ENV | Environment mode | Optional | `production` |
| PORT | Application port | Optional | `5001` |
| SECRET_KEY | Encryption secret | **Recommended** | `CHANGE_ME_IN_PRODUCTION` |
| GNUPGHOME | GnuPG home directory | Optional | `/home/appuser/.gnupg` |
| KEYS_DIR | Path to store generated keys | Optional | `/app/keys` |

### Security Recommendations

1. Always generate a unique `SECRET_KEY`
2. Use persistent volumes for key storage
3. Limit network access to the container
4. Regularly update the offline image

### Accessing the Application

- Web Interface: `http://localhost:5001`
- Health Check: `http://localhost:5001/health`

### Troubleshooting

- Check container logs: 
  ```bash
  docker logs key-generator
  ```
- Verify container status:
  ```bash
  docker ps | grep key-generator
  ```

## Offline Key Generation Examples

### SSH Key
```bash
curl -X POST http://localhost:5001/generate/ssh \
  -H "Content-Type: application/json" \
  -d '{
    "keyType": "ed25519",
    "comment": "offline-user@example.com"
  }'
```

### RSA Key
```bash
curl -X POST http://localhost:5001/generate/rsa \
  -H "Content-Type: application/json" \
  -d '{
    "keySize": 4096,
    "passphrase": "optional-secure-passphrase"
  }'
```

### Passphrase Generation
```bash
curl -X POST http://localhost:5001/generate/passphrase \
  -H "Content-Type: application/json" \
  -d '{
    "length": 24,
    "includeNumbers": true,
    "includeSpecial": true
  }'
```
