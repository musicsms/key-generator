# Key Generator

A secure web-based tool for generating various types of cryptographic key pairs with custom comments and organized storage.

## Features

- Generate multiple types of cryptographic keys:
  - SSH Keys (RSA, ECDSA, ED25519)
  - RSA Keys
  - PGP Keys (RSA and ECC)
  - Secure Passphrases
- Key Generation Features:
  - Custom comments for key organization
  - Optional passphrase protection
  - Flexible key options (key size, curve type)
  - Configurable expiration for PGP keys
- Modern Web Interface:
  - Clean Bootstrap-based UI
  - Password visibility toggle
  - One-click copy to clipboard
  - Organized key display
  - Real-time form validation
- Secure Storage:
  - Organized directory structure
  - Secure key handling
  - Clear error messaging

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended)
- Required system packages for PGP:
  - GnuPG (gpg)

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

## Usage

### Generating SSH Keys
1. Select the SSH tab
2. Choose key type (RSA, ECDSA, ED25519)
3. Set key size (for RSA)
4. Add an optional comment and passphrase
5. Click "Generate SSH Key"

### Generating PGP Keys
1. Select the PGP tab
2. Enter name and email
3. Choose key type (RSA or ECC)
4. Select key length (RSA) or curve type (ECC)
5. Set expiration time (or never expire)
6. Add an optional passphrase
7. Click "Generate PGP Key"

### Generating RSA Keys
1. Select the RSA tab
2. Choose key size
3. Add an optional comment and passphrase
4. Click "Generate RSA Key"

### Generating Secure Passphrases
1. Select the Passphrase tab
2. Set desired length
3. Configure character options
4. Click "Generate Passphrase"

## Security Notes

- All keys are generated server-side for enhanced security
- Passphrases are strongly recommended for private keys
- Private keys are never stored in browser storage
- All communications are handled over secure connections
- Keys are stored in an organized directory structure

## API Response Format

### Success Response
```json
{
    "success": true,
    "data": {
        "privateKey": "-----BEGIN PRIVATE KEY-----\n...",
        "publicKey": "ssh-rsa AAAA...",
        "directory": "/path/to/keys"
    }
}
```

### Error Response
```json
{
    "success": false,
    "error_message": "Description of what went wrong"
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
