# Key Generator

[![CI/CD Pipeline](https://github.com/musicsms/key-generator/actions/workflows/ci-cd.yml/badge.svg?branch=dev)](https://github.com/musicsms/key-generator/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/musicsms/key-generator/branch/dev/graph/badge.svg)](https://codecov.io/gh/musicsms/key-generator)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://github.com/musicsms/key-generator/pkgs/container/key-generator)

A secure web-based tool for generating various types of cryptographic key pairs with custom comments and organized storage.

## Features

- Generate multiple types of cryptographic keys:
  - SSH Keys (RSA, ECDSA, ED25519)
  - RSA Keys (2048, 3072, 4096 bits)
  - PGP Keys (RSA, ECC)
- Custom comments for key organization
- Secure key storage with organized directory structure
- Optional passphrase protection
- Modern web interface with Bootstrap
- Docker support for easy deployment
- Comprehensive security checks with Bandit
- Automated testing and CI/CD pipeline

## Prerequisites

1. Python 3.12 or higher
2. pip (Python package manager)
3. GnuPG (GPG) for PGP key generation
4. Docker (optional, for containerized deployment)

## Quick Start

### Using Docker

```bash
# Pull the latest image
docker pull ghcr.io/musicsms/key-generator:latest

# Run the container
docker run -d -p 5001:5001 ghcr.io/musicsms/key-generator:latest
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/musicsms/key-generator.git
cd key-generator

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application will be available at http://localhost:5001

## Development

1. Create a new branch from dev:
```bash
git checkout -b feature/your-feature dev
```

2. Make your changes and run tests:
```bash
pip install -r requirements.txt
pytest
```

3. Create a pull request to the dev branch

## Security

- All cryptographic operations use standard libraries and tools
- Debug mode is disabled by default
- Regular security scans with Bandit
- Secure subprocess handling for GPG operations
- Environment-based configuration

## Documentation

- [API Documentation](API.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
