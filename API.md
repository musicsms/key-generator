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
    "type": "rsa",           // Required: "rsa", "ecdsa", or "ed25519"
    "bits": 4096,           // Optional for RSA (2048, 3072, 4096), ignored for others
    "curve": "prime256v1",  // Required for ECDSA, ignored for others
    "comment": "work_key",  // Optional
    "passphrase": "secure"  // Optional
}
```

#### Response

```json
{
    "success": true,
    "data": {
        "privateKey": "-----BEGIN OPENSSH PRIVATE KEY-----\n...",
        "publicKey": "ssh-rsa AAAA..."
    }
}
```

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
    "name": "John Doe",     // Required
    "email": "john@example.com",  // Required
    "comment": "work_key",  // Optional
    "key_type": "RSA",     // Optional: "RSA" or "ECC"
    "key_length": 4096,    // Optional for RSA (2048, 3072, 4096)
    "curve": "prime256v1", // Required for ECC
    "passphrase": "secure", // Optional
    "expire_time": "2y"    // Optional, format: number + y/m/d (e.g., "2y", "6m", "90d")
}
```

#### Response

```json
{
    "success": true,
    "data": {
        "privateKey": "-----BEGIN PGP PRIVATE KEY BLOCK-----\n...",
        "publicKey": "-----BEGIN PGP PUBLIC KEY BLOCK-----\n..."
    }
}
```

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
