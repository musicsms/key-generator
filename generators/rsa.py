from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from utils.response import success_response, error_response

def generate_rsa_key(key_size=2048, passphrase=None):
    """Generate an RSA key pair"""
    try:
        # Validate key size
        if key_size not in [1024, 2048, 4096]:
            return error_response('Invalid key size. Must be 1024, 2048, or 4096')
            
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize private key
        # Only use encryption if passphrase is not None/empty
        if passphrase and isinstance(passphrase, str) and passphrase.strip():
            encryption = serialization.BestAvailableEncryption(passphrase.encode('utf-8'))
        else:
            encryption = serialization.NoEncryption()
            
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
        
        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return success_response({
            'publicKey': public_pem.decode('utf-8'),
            'privateKey': private_pem.decode('utf-8')
        })
        
    except Exception as e:
        return error_response(f'Failed to generate RSA key pair: {str(e)}')
