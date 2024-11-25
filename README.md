# Key Generator Web Application

A secure web application for generating various types of cryptographic keys with a user-friendly interface.

## Features

- Generate SSH keys with customizable options
- Generate RSA key pairs with optional passphrase protection
- Modern and responsive UI using Bootstrap 5
- Secure key generation using industry-standard cryptographic libraries
- Copy-to-clipboard functionality for easy key access

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
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

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Use the web interface to:
   - Generate SSH keys
   - Generate RSA key pairs
   - Copy generated keys to clipboard
   - Save keys to files

## Security Considerations

- All key generation is performed server-side using secure cryptographic libraries
- Passphrases are never stored and are only used for key encryption
- Generated keys are not stored on the server
- HTTPS is recommended for production deployment

## Development

- Python 3.10+ required
- Flask for backend API
- Bootstrap 5.3.2 for frontend UI
- Cryptography library for secure key generation

## License

[Your chosen license]
