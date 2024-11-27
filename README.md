# Key Generator

A secure web-based tool for generating various types of cryptographic key pairs with custom comments and organized storage.

## CI/CD Status

### Functional Tests
[![Function Tests](https://github.com/musicsms/key-generator/actions/workflows/test.yml/badge.svg)](https://github.com/musicsms/key-generator/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/musicsms/key-generator/branch/main/graph/badge.svg)](https://codecov.io/gh/musicsms/key-generator)

### Security Status
[![Security Scan](https://github.com/musicsms/key-generator/actions/workflows/security.yml/badge.svg)](https://github.com/musicsms/key-generator/actions/workflows/security.yml)
[![Known Vulnerabilities](https://snyk.io/test/github/musicsms/key-generator/badge.svg)](https://snyk.io/test/github/musicsms/key-generator)
[![Docker Scout](https://img.shields.io/badge/docker%20scout-monitored-blue)](https://scout.docker.com/image/docker.io/musicsms/key-generator)
[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)

## Security Status

| Component | Status | Details |
|-----------|--------|---------|
| Base Image | Clean | python:3.13-alpine |
| Dependencies | Monitored | Continuously scanned by Snyk |
| Code Quality | Analyzed | Bandit security checks |
| Container | Secured | Non-root user, minimal permissions |
| Updates | Automated | Weekly security patches |

Security Features:
- Non-root container execution
- Regular dependency updates
- Multi-stage builds to minimize attack surface
- Automated vulnerability scanning
- Security patches through Docker Scout
- Static code analysis with Bandit
- Runtime security monitoring

## Features

- Generate multiple types of cryptographic keys:
  - SSH Keys (RSA, ECDSA, ED25519)
  - RSA Keys (2048/4096 bits)
  - PGP Keys
  - Passphrase Generation
- Custom comments for key organization
- Secure key storage with organized directory structure
- Optional passphrase protection
- Modern web interface
- Docker multi-arch support (AMD64/ARM64)
- Health check endpoints
- Comprehensive test coverage

## Prerequisites

1. Python 3.13 or higher
2. pip (Python package manager)
3. virtualenv (recommended)
4. GnuPG (GPG) installation:
   - Windows: Download and install [Gpg4win](https://www.gpg4win.org)
   - macOS: Install using Homebrew: `brew install gnupg`
   - Linux: Install using package manager: `apt-get install gnupg` or equivalent

## Quick Start with Docker

```bash
# Pull the latest image (automatically selects your architecture)
docker pull musicsms/key-generator:latest

# Run with Docker
docker run -d \
  --name key-generator \
  -p 5001:5001 \
  -e FLASK_ENV=production \
  -v key-storage:/app/keys \
  -v gpg-home:/home/appuser/.gnupg \
  musicsms/key-generator:latest
```

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/musicsms/key-generator.git
cd key-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
# Development mode
FLASK_ENV=development python app.py

# Production mode
FLASK_ENV=production python app.py
```

## Production Deployment

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| FLASK_ENV | Environment mode | `production` | Optional |
| FLASK_APP | Flask application entry | `app.py` | Optional |
| PORT | Application port | `5001` | Optional |
| SECRET_KEY | Encryption secret | `CHANGE_ME_IN_PRODUCTION` | **Recommended** |
| GNUPGHOME | GnuPG home directory | `/home/appuser/.gnupg` | Optional |
| KEYS_DIR | Path to store generated keys | `/app/keys` | Optional |

### Security Recommendations

1. Always use HTTPS in production
2. Set a strong, unique `SECRET_KEY`
3. Use Docker volumes for persistent storage
4. Keep base image and dependencies updated
5. Monitor security scans
6. Enable Docker content trust

### Health Monitoring

The application provides a health check endpoint at `/health`:
```json
{
  "status": "healthy"
}
```

## API Endpoints

### Generate SSH Key
```bash
curl -X POST http://localhost:5001/generate/ssh \
  -H "Content-Type: application/json" \
  -d '{
    "keyType": "ed25519",
    "comment": "user@example.com"
  }'
```

### Generate RSA Key
```bash
curl -X POST http://localhost:5001/generate/rsa \
  -H "Content-Type: application/json" \
  -d '{
    "keySize": 4096,
    "passphrase": "optional-secure-passphrase"
  }'
```

### Generate Passphrase
```bash
curl -X POST http://localhost:5001/generate/passphrase \
  -H "Content-Type: application/json" \
  -d '{
    "length": 24,
    "includeNumbers": true,
    "includeSpecial": true
  }'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `pytest tests/ -v`
4. Submit a pull request

## License

MIT License - see LICENSE file for details
