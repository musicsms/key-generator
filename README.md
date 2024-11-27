# Key Generator

[![Tests](https://github.com/musicsms/key-generator/actions/workflows/test.yml/badge.svg)](https://github.com/musicsms/key-generator/actions/workflows/test.yml)
[![CodeQL](https://github.com/musicsms/key-generator/actions/workflows/codeql.yml/badge.svg)](https://github.com/musicsms/key-generator/actions/workflows/codeql.yml)
[![Security Scan](https://github.com/musicsms/key-generator/actions/workflows/security.yml/badge.svg)](https://github.com/musicsms/key-generator/actions/workflows/security.yml)
[![Docker Build](https://github.com/musicsms/key-generator/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/musicsms/key-generator/actions/workflows/docker-publish.yml)

A secure web-based tool for generating various types of cryptographic key pairs with custom comments and organized storage.

## Features

- Generate multiple types of cryptographic keys:
  - SSH Keys (RSA, ECDSA, ED25519)
  - RSA Keys (2048, 4096 bits)
  - PGP Keys
  - Secure Passphrases
- Custom comments for key organization
- Secure key storage with organized directory structure
- Optional passphrase protection
- Modern web interface with Bootstrap
- Comprehensive test coverage
- Docker and Kubernetes support
- Security scanning and CodeQL analysis

## Prerequisites

1. Python 3.13 or higher
2. pip (Python package manager)
3. virtualenv (recommended)
4. GnuPG (GPG) installation:
   - Windows: Download and install [Gpg4win](https://www.gpg4win.org)
   - macOS: Install using Homebrew: `brew install gnupg`
   - Linux: Install using package manager: `apt-get install gnupg` or equivalent

## Installation

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

## Development Setup

1. Run the Flask development server:
```bash
python app.py
```

2. Access the application at `http://localhost:5000`

## Testing

Run the test suite:
```bash
pytest tests/
```

For coverage report:
```bash
pytest --cov=. tests/
```

## Production Deployment

### Using Docker (Recommended)

1. Build the Docker image:
```bash
docker build -t key-generator:latest .
```

2. Run with Docker:
```bash
docker run -d \
  --name key-generator \
  -p 5000:5000 \
  -v key-storage:/app/keys \
  key-generator:latest
```

3. Or use Docker Compose:
```bash
docker-compose up -d
```

The application will be available at `http://localhost:5000`

### Using Kubernetes

1. Create namespace and resources:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

2. Access the service:
```bash
kubectl port-forward -n key-generator svc/key-generator 5000:5000
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_APP` | Flask application entry point | `app.py` |
| `FLASK_ENV` | Flask environment | `production` |
| `KEY_STORAGE_PATH` | Path to store generated keys | `/app/keys` |
| `GNUPGHOME` | GnuPG home directory | `/app/keys/.gnupg` |

## Security Features

- Alpine-based minimal Docker image
- Regular security scanning with CodeQL
- Bandit security linting
- SARIF security reports
- Secure file permissions
- Input validation and sanitization
- No sensitive data in version control

## Continuous Integration

The following checks run on every push and pull request:

- Unit Tests (pytest)
- Integration Tests
- CodeQL Analysis
- Security Scanning (Bandit)
- Docker Build and Push
- Code Coverage Report

## API Documentation

For API documentation and examples, see [API.md](API.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
