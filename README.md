# WindSurf Key Generator

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

- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)

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

2. Access the application at `http://localhost:5000`

## Production Deployment

### Using Gunicorn (Recommended)

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
ExecStart=/path/to/key-generator/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app

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
        proxy_pass http://127.0.0.1:8000;
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
