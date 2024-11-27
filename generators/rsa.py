"""RSA key generation module."""

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from utils.response import info_response, error_response
from utils.sanitize import validate_comment
import logging

logger = logging.getLogger(__name__)

def generate_rsa_key(key_size=2048, comment=None, passphrase=None):
    """
    Generate an RSA key pair.
    
    Args:
        key_size (int): Size of the key in bits (2048, 3072, or 4096)
        comment (str, optional): Comment to add to the key
        passphrase (str, optional): Passphrase to protect the private key
        
    Returns:
        dict: Response containing the generated keys and status

    Raises:
        ValueError: If input parameters are invalid.
        Exception: If key generation fails.
    """
    try:
        # Validate key size
        if key_size not in [2048, 3072, 4096]:
            raise ValueError("Invalid key size. Must be 2048, 3072, or 4096 bits")

        # Validate and sanitize comment if provided
        try:
            if comment:
                comment = validate_comment(comment)
        except ValueError as e:
            raise ValueError(str(e))

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
        
        logger.info("RSA key pair generated")
        return info_response({
            'publicKey': public_pem.decode('utf-8'),
            'privateKey': private_pem.decode('utf-8')
        })
        
    except ValueError as e:
        logger.error("Invalid input parameters: %s", str(e))
        return error_response(str(e))
    except Exception as e:
        logger.error("Failed to generate RSA key pair: %s", str(e))
        return error_response(f'Failed to generate RSA key pair: {str(e)}')
