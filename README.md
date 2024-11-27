#   Key Generator

A secure web-based tool for generating various types of cryptographic key pairs with custom comments and organized storage.

## Features

- Generate multiple types of cryptographic keys:
  - SSH Keys (RSA, ECDSA, ED25519)
  - RSA Keys
  - PGP Keys (coming soon)
- Custom comments for key organization
- Secure key storage with organized directory structure
- Optional passphrase protection
- Modern web interface with Bootstrap

## Prerequisites

1. Python 3.8 or higher
2. pip (Python package manager)
3. virtualenv (recommended)
4. GnuPG (GPG) installation:
   - Windows: Download and install [Gpg4win](https://www.gpg4win.org)
   - macOS: Install using Homebrew: `brew install gnupg`
   - Linux: Install using package manager: `apt-get install gnupg` or equivalent

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/key-generator.git
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

2. Access the application at `http://localhost:5001`

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
  -p 5001:5001 \
  -v ./keys:/app/keys \
  key-generator:latest
```

3. Or use Docker Compose:
```bash
docker-compose up -d
```

The application will be available at `http://localhost:5001`

For offline deployment instructions, see [docker-offline.md](docker-offline.md).

### Using Gunicorn (Alternative)

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Create a systemd service file (on Linux):
```bash
sudo nano /etc/systemd/system/key-generator.service
```

Add the following content:
```ini
[Unit]
Description=Key Generator Web Application
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/key-generator
Environment="PATH=/path/to/key-generator/venv/bin"
ExecStart=/path/to/key-generator/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 app:app

[Install]
WantedBy=multi-user.target
```

3. Start and enable the service:
```bash
sudo systemctl start key-generator
sudo systemctl enable key-generator
```

### Nginx Configuration

1. Install Nginx:
```bash
sudo apt install nginx  # For Ubuntu/Debian
```

2. Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/key-generator
```

Add the following content:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/key-generator/static;
    }
}
```

3. Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/key-generator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Security Considerations

1. Set up SSL/TLS:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

2. Set proper permissions:
```bash
chmod 700 /path/to/key-generator/keys
```

3. Configure firewall:
```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Usage

1. Access the web interface through your domain
2. Select the type of key you want to generate
3. Enter a comment (optional) to organize your keys
4. Add a passphrase (optional) for additional security
5. Generate the key pair
6. Keys will be stored in the `keys/[comment]` directory

## API Documentation

The Key Generator provides a RESTful API for generating different types of cryptographic keys. All requests should be made with Content-Type: `application/json`.

### Endpoints

#### 1. Generate SSH Key
```http
POST /generate/ssh
```

Request Body:
```json
{
    "comment": "github_key",          // Optional, max 40 chars, no spaces
    "keyType": "rsa",                // Options: "rsa", "ecdsa", "ed25519"
    "keySize": 2048,                 // For RSA: 2048, 4096; For ECDSA: 256, 384, 521
    "passphrase": "your_passphrase"  // Optional
}
```

Response:
```json
{
    "success": true,
    "data": {
        "privateKey": "-----BEGIN PRIVATE KEY-----\n...",
        "publicKey": "ssh-rsa AAAA...",
        "keyType": "rsa",
        "keySize": 2048,
        "directory": "keys/github_key"
    }
}
```

#### 2. Generate RSA Key
```http
POST /generate/rsa
```

Request Body:
```json
{
    "comment": "api_key",            // Optional, max 40 chars, no spaces
    "keySize": 2048,                 // Options: 2048, 4096
    "passphrase": "your_passphrase"  // Optional
}
```

Response:
```json
{
    "success": true,
    "data": {
        "privateKey": "-----BEGIN PRIVATE KEY-----\n...",
        "publicKey": "-----BEGIN PUBLIC KEY-----\n...",
        "keySize": 2048,
        "directory": "keys/api_key"
    }
}
```

#### 3. Generate Passphrase
```http
POST /generate/passphrase
```

Request Body:
```json
{
    "length": 16,                    // Optional, default: 16, range: 8-64
    "includeNumbers": true,          // Optional, default: true
    "includeSpecial": true,          // Optional, default: true
    "excludeChars": "@#$%"          // Optional, characters to exclude
}
```

Response:
```json
{
    "success": true,
    "data": {
        "passphrase": "xK9#mP2$vL5nQ8"
    }
}
```

### Error Responses

All endpoints return error responses in this format:
```json
{
    "success": false,
    "error_message": "Description of what went wrong"
}
```

Common error status codes:
- 400: Bad Request (invalid parameters)
- 500: Internal Server Error

### Example Usage

Using curl:
```bash
# Generate SSH Key
curl -X POST http://your-domain.com/generate/ssh \
  -H "Content-Type: application/json" \
  -d '{"comment": "github_key", "keyType": "rsa", "keySize": 2048}'

# Generate RSA Key
curl -X POST http://your-domain.com/generate/rsa \
  -H "Content-Type: application/json" \
  -d '{"comment": "api_key", "keySize": 2048}'

# Generate Passphrase
curl -X POST http://your-domain.com/generate/passphrase \
  -H "Content-Type: application/json" \
  -d '{"length": 16, "includeNumbers": true, "includeSpecial": true}'
```

Using Python requests:
```python
import requests

# Generate SSH Key
response = requests.post(
    'http://your-domain.com/generate/ssh',
    json={
        'comment': 'github_key',
        'keyType': 'rsa',
        'keySize': 2048
    }
)
print(response.json())

# Generate RSA Key
response = requests.post(
    'http://your-domain.com/generate/rsa',
    json={
        'comment': 'api_key',
        'keySize': 2048
    }
)
print(response.json())

# Generate Passphrase
response = requests.post(
    'http://your-domain.com/generate/passphrase',
    json={
        'length': 16,
        'includeNumbers': True,
        'includeSpecial': True
    }
)
print(response.json())
```

### Security Considerations for API Usage

1. Always use HTTPS in production
2. Store generated keys securely
3. Never log or display private keys in plaintext
4. Consider implementing API authentication for production use
5. Rate limit requests to prevent abuse

## API Usage Examples

### Using curl

1. Generate SSH Key (RSA)
```bash
# Basic RSA key
curl -X POST http://localhost:5001/generate/ssh \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "github_key",
    "keyType": "rsa",
    "keySize": 2048
  }'

# ED25519 key with passphrase
curl -X POST http://localhost:5001/generate/ssh \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "secure_server",
    "keyType": "ed25519",
    "passphrase": "your-secure-passphrase"
  }'

# ECDSA key with custom size
curl -X POST http://localhost:5001/generate/ssh \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "ecdsa_key",
    "keyType": "ecdsa",
    "keySize": 384
  }'
```

2. Generate RSA Key
```bash
# Standard RSA key
curl -X POST http://localhost:5001/generate/rsa \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "api_key",
    "keySize": 2048
  }'

# RSA key with passphrase
curl -X POST http://localhost:5001/generate/rsa \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "secure_api_key",
    "keySize": 4096,
    "passphrase": "your-secure-passphrase"
  }'
```

3. Generate Passphrase
```bash
# Basic passphrase
curl -X POST http://localhost:5001/generate/passphrase \
  -H "Content-Type: application/json" \
  -d '{
    "length": 16,
    "includeNumbers": true,
    "includeSpecial": true
  }'

# Custom passphrase with excluded characters
curl -X POST http://localhost:5001/generate/passphrase \
  -H "Content-Type: application/json" \
  -d '{
    "length": 24,
    "includeNumbers": true,
    "includeSpecial": true,
    "excludeChars": "@#$%"
  }'
```

### Using Python requests

```python
import requests
import json

BASE_URL = "http://localhost:5001"

def generate_ssh_key():
    response = requests.post(
        f"{BASE_URL}/generate/ssh",
        json={
            "comment": "github_key",
            "keyType": "rsa",
            "keySize": 2048
        }
    )
    return response.json()

def generate_rsa_key():
    response = requests.post(
        f"{BASE_URL}/generate/rsa",
        json={
            "comment": "api_key",
            "keySize": 4096,
            "passphrase": "optional-passphrase"
        }
    )
    return response.json()

def generate_passphrase():
    response = requests.post(
        f"{BASE_URL}/generate/passphrase",
        json={
            "length": 16,
            "includeNumbers": True,
            "includeSpecial": True
        }
    )
    return response.json()

# Example usage
if __name__ == "__main__":
    # Generate SSH key
    ssh_key = generate_ssh_key()
    if ssh_key["success"]:
        print("SSH Key:", ssh_key["data"]["publicKey"])
    
    # Generate RSA key
    rsa_key = generate_rsa_key()
    if rsa_key["success"]:
        print("RSA Key:", rsa_key["data"]["publicKey"])
    
    # Generate passphrase
    passphrase = generate_passphrase()
    if passphrase["success"]:
        print("Passphrase:", passphrase["data"]["passphrase"])
```

### Example Response Formats

1. Successful SSH Key Generation:
```json
{
  "success": true,
  "data": {
    "privateKey": "-----BEGIN PRIVATE KEY-----\n...",
    "publicKey": "ssh-rsa AAAA...",
    "keyType": "rsa",
    "keySize": 2048,
    "directory": "keys/github_key"
  }
}
```

2. Successful RSA Key Generation:
```json
{
  "success": true,
  "data": {
    "privateKey": "-----BEGIN PRIVATE KEY-----\n...",
    "publicKey": "-----BEGIN PUBLIC KEY-----\n...",
    "keySize": 2048,
    "directory": "keys/api_key"
  }
}
```

3. Successful Passphrase Generation:
```json
{
  "success": true,
  "data": {
    "passphrase": "xK9#mP2$vL5nQ8",
    "length": 16,
    "includeNumbers": true,
    "includeSpecial": true
  }
}
```

4. Error Response:
```json
{
  "success": false,
  "error_message": "Invalid key size. Supported sizes for RSA: 2048, 4096"
}
```

### Common Error Cases

1. Invalid Key Type:
```bash
curl -X POST http://localhost:5001/generate/ssh \
  -H "Content-Type: application/json" \
  -d '{"keyType": "invalid"}'
# Response: {"success": false, "error_message": "Invalid key type. Supported types: rsa, ecdsa, ed25519"}
```

2. Invalid Key Size:
```bash
curl -X POST http://localhost:5001/generate/rsa \
  -H "Content-Type: application/json" \
  -d '{"keySize": 1024}'
# Response: {"success": false, "error_message": "Invalid key size. Supported sizes: 2048, 4096"}
```

3. Invalid Comment:
```bash
curl -X POST http://localhost:5001/generate/ssh \
  -H "Content-Type: application/json" \
  -d '{"comment": "invalid space"}'
# Response: {"success": false, "error_message": "Comment cannot contain spaces"}
```

### API Security Best Practices

1. Always use HTTPS in production
2. Store private keys securely
3. Use strong passphrases
4. Never log private keys
5. Implement rate limiting for production use
6. Consider adding API authentication

## Directory Structure
```
key-generator/
├── app.py                  # Main Flask application
├── generators/             # Key generation modules
├── static/                # Static files (JS, CSS)
├── utils/                 # Utility functions
└── templates/             # HTML templates
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)

## Support

For support, please open an issue in the GitHub repository.
