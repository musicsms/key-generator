# Key Generator API Documentation

## Base URL

```
http://localhost:5001
```

## Endpoints

### Health Check

```http
GET /health
```

Returns the health status of the API.

#### Response

```json
{
    "status": "healthy"
}
```

### Generate Passphrase

```http
POST /generate/passphrase
```

Generates a secure passphrase.

#### Request Body

```json
{
    "length": 16,  // Optional, default: 16
    "words": 4     // Optional, default: 4
}
```

#### Response

```json
{
    "success": true,
    "data": {
        "passphrase": "correct-horse-battery-staple"
    }
}
```

### Generate SSH Key

```http
POST /generate/ssh
```

Generates an SSH key pair.

#### Request Body

```json
{
    "keyType": "rsa",          // Required: "rsa", "ecdsa", or "ed25519"
    "keySize": 4096,           // Optional for RSA (2048, 4096), ECDSA (256, 384, 521)
    "comment": "work_key",     // Optional
    "passphrase": "secure"     // Optional, if provided the private key will be encrypted
}
```

#### Response

```json
{
    "success": true,
    "data": {
        "privateKey": "-----BEGIN ENCRYPTED PRIVATE KEY-----\n...", // PKCS8 format if passphrase provided
        "publicKey": "ssh-rsa AAAA... work_key",
        "keyType": "rsa",
        "keySize": 4096,
        "comment": "work_key"
    }
}
```

Note: When a passphrase is provided, the private key will be encrypted using PKCS8 format. Without a passphrase, the key will be in OpenSSH format.

### Generate RSA Key

```http
POST /generate/rsa
```

Generates an RSA key pair.

#### Request Body

```json
{
    "bits": 4096,           // Optional (2048, 3072, 4096)
    "comment": "work_key",  // Optional
    "passphrase": "secure"  // Optional
}
```

#### Response

```json
{
    "success": true,
    "data": {
        "privateKey": "-----BEGIN PRIVATE KEY-----\n...",
        "publicKey": "-----BEGIN PUBLIC KEY-----\n..."
    }
}
```

### Generate PGP Key

```http
POST /generate/pgp
```

Generates a PGP key pair.

#### Request Body

```json
{
    "name": "John Doe",         // Required
    "email": "john@example.com",// Required
    "comment": "work_key",      // Optional
    "keyType": "RSA",          // Optional: "RSA" (default) or "ECC"
    "keyLength": 4096,         // Optional for RSA (2048, 4096)
    "passphrase": "secure",     // Optional but recommended
    "expireTime": "never"      // Optional, default: "never", or format: "1y", "2y", "3y", "5y"
}
```

#### Response

```json
{
    "success": true,
    "data": {
        "privateKey": "-----BEGIN PGP PRIVATE KEY BLOCK-----\n...",
        "publicKey": "-----BEGIN PGP PUBLIC KEY BLOCK-----\n...",
        "keyId": "0123456789ABCDEF",
        "keyType": "RSA",
        "keyLength": 4096,
        "name": "John Doe",
        "email": "john@example.com",
        "comment": "work_key",
        "expireDate": "0"
    }
}
```

Note: When expireTime is set to "never", the key will not have an expiration date. For other values, specify the number of years (e.g., "1y", "2y", etc.).

## Error Responses

All endpoints return error responses in the following format:

```json
{
    "success": false,
    "error": {
        "message": "Error description",
        "code": "ERROR_CODE"
    }
}
```

Common error codes:
- `INVALID_INPUT`: Invalid request parameters
- `KEY_GENERATION_ERROR`: Error during key generation
- `SYSTEM_ERROR`: Internal server error

## Security Considerations

1. All endpoints use HTTPS in production
2. API rate limiting is recommended in production
3. Key generation is performed server-side using secure libraries
4. Passphrases are never stored
5. Generated keys are stored securely and accessible only to authorized users
