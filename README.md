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
- Custom comments for key organization
- Secure key storage with organized directory structure
- Optional passphrase protection
- Modern web interface with Bootstrap
- Docker multi-arch support (AMD64/ARM64)
- Health check endpoints
- Comprehensive test coverage

## Testing

### Functional Testing
The project includes comprehensive test coverage:
- Unit tests for all key generation functions
- Integration tests for API endpoints
- Environment and configuration tests
- Error handling and edge cases

Run tests locally:
```bash
pytest tests/ -v --cov=./ --cov-report=term-missing
```

### Security Testing
Security scanning is performed automatically:
- Snyk vulnerability scanning (requires `SNYK_TOKEN`)
- Bandit static code analysis
- GitHub CodeQL analysis
- Weekly scheduled security scans

To enable Snyk scanning:
1. Create a Snyk account at https://snyk.io
2. Generate a Snyk API token
3. Add the token as `SNYK_TOKEN` in your GitHub repository secrets

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
  -v key-storage:/app/keys \
  -v gpg-home:/home/appuser/.gnupg \
  musicsms/key-generator:latest

# Or use Docker Compose
docker-compose up -d
```

The application will be available at `http://localhost:5001`

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

4. Run tests:
```bash
pytest tests/ -v
```

5. Start the development server:
```bash
python app.py
```

## Production Deployment

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_APP | Flask application entry | app.py |
| FLASK_ENV | Environment (production/development) | production |
| PORT | Application port | 5001 |
| GNUPGHOME | GnuPG home directory | /home/appuser/.gnupg |
| KEY_STORAGE_PATH | Path to store generated keys | /app/keys |

### Docker Volumes

| Volume | Purpose | Path |
|--------|---------|------|
| key-storage | Store generated keys | /app/keys |
| gpg-home | GnuPG configuration | /home/appuser/.gnupg |

### Security Recommendations

1. Always use HTTPS in production
2. Set up proper firewall rules
3. Use Docker volumes instead of bind mounts
4. Keep the base image updated
5. Monitor security scans in Docker Scout
6. Review Snyk security reports
7. Enable Docker content trust

### Health Monitoring

The application provides a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "version": "1.0.8",
  "timestamp": "2024-01-20T12:00:00Z"
}
```

## API Documentation

### Generate SSH Key
```bash
curl -X POST http://localhost:5001/generate/ssh \
  -H "Content-Type: application/json" \
  -d '{
    "key_type": "ed25519",
    "comment": "user@example.com"
  }'
```

### Generate RSA Key
```bash
curl -X POST http://localhost:5001/generate/rsa \
  -H "Content-Type: application/json" \
  -d '{
    "key_size": 4096,
    "passphrase": "optional-secure-passphrase"
  }'
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `pytest tests/ -v`
4. Submit a pull request

## License

MIT License - see LICENSE file for details
