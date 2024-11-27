"""
SSH Key Generation Module.
Provides functionality to generate SSH keys with various algorithms and sizes.
"""

import os
import logging
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519
from cryptography.hazmat.primitives.asymmetric.ec import SECP384R1
from utils.response import info_response, error_response
from utils.sanitize import validate_comment
from utils.utils import create_output_directory, save_key_pair

# Configure logging
logger = logging.getLogger(__name__)

# Ensure proper encoding is set
os.environ['LC_ALL'] = 'en_US.UTF-8'
os.environ['LANG'] = 'en_US.UTF-8'

def generate_ssh_key(key_type="ed25519", key_size=None, comment=None, passphrase=None):
    """
    Generate an SSH key pair with specified parameters.
    
    Args:
        key_type (str): Type of key to generate (rsa, ecdsa, ed25519)
        key_size (int, optional): Key size for RSA keys (2048, 3072, or 4096 bits)
        comment (str, optional): Comment to add to the key
        passphrase (str, optional): Passphrase to protect the private key
        
    Returns:
        dict: Response containing the generated keys and status
        
    Raises:
        ValueError: If invalid parameters are provided
        OSError: If key generation fails
    """
    try:
        # Validate key type
        key_type = key_type.lower()
        if key_type not in ["rsa", "ecdsa", "ed25519"]:
            raise ValueError("Invalid key type. Must be 'rsa', 'ecdsa', or 'ed25519'")

        # Validate and sanitize comment if provided
        try:
            if comment:
                comment = validate_comment(comment)
        except ValueError as e:
            return error_response(str(e))

        # Set encryption algorithm if passphrase is provided
        encryption = (serialization.BestAvailableEncryption(passphrase.encode()) 
                     if passphrase else serialization.NoEncryption())
        
        # Generate key based on type
        if key_type == 'rsa':
            if not key_size:
                key_size = 4096
            elif key_size not in [2048, 3072, 4096]:
                raise ValueError("Invalid key size. Must be 2048, 3072, or 4096 bits")
            
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
        
        elif key_type == 'ecdsa':
            # Use SECP384R1 curve for ECDSA (NIST P-384)
            private_key = ec.generate_private_key(SECP384R1())
        
        elif key_type == 'ed25519':
            # Ed25519 has fixed key size and is recommended
            private_key = ed25519.Ed25519PrivateKey.generate()
        
        # Serialize keys
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=encryption
        )
        
        public_key = private_key.public_key()
        public_key_ssh = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )
        
        # Add comment to public key if provided
        public_key_str = public_key_ssh.decode()
        if comment:
            public_key_str += f' {comment}'
        
        dir_path = create_output_directory(key_type, comment)
        private_key, public_key = save_key_pair(private_key_pem.decode(), public_key_str, dir_path, key_type)

        logger.info("SSH key pair generated and saved in %s", dir_path)
        return info_response({
            'privateKey': private_key,
            'publicKey': public_key,
            'keyType': key_type,
            'keySize': key_size if key_type == 'rsa' else None,
            'comment': comment
        })
        
    except ValueError as e:
        return error_response(str(e))
    except OSError as e:
        logger.error("Failed to generate SSH key pair: %s", str(e))
        return error_response("Failed to generate SSH key pair")
    except Exception as e:
        logger.error("SSH Key Generation Error: %s", str(e))
        return error_response("Failed to generate SSH key pair")
