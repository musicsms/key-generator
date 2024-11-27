import os
import sys
import uuid
import traceback
import paramiko
from utils.response import info_response, error_response
from utils.sanitize import validate_comment

# Ensure proper encoding is set
os.environ['LC_ALL'] = 'en_US.UTF-8'
os.environ['LANG'] = 'en_US.UTF-8'

from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519
from cryptography.hazmat.primitives import serialization

def generate_ssh_key(key_type="rsa", key_size=2048, comment=None, passphrase=None):
    """
    Generate an SSH key pair.
    
    Args:
        key_type (str): Type of key to generate (rsa, ecdsa, ed25519)
        key_size (int): Key size for RSA/ECDSA keys
        comment (str, optional): Comment to add to the key
        passphrase (str, optional): Passphrase to protect the private key
        
    Returns:
        dict: Response containing the generated keys and status
    """
    try:
        # Validate key type
        key_type = key_type.lower()
        if key_type not in ["rsa", "ecdsa", "ed25519"]:
            return error_response("Invalid key type. Must be 'rsa', 'ecdsa', or 'ed25519'")

        # Validate and sanitize comment if provided
        try:
            if comment:
                comment = validate_comment(comment)
        except ValueError as e:
            return error_response(str(e))

        # Validate key size based on type
        if key_type == 'rsa':
            if key_size not in [2048, 4096]:
                raise ValueError("RSA key size must be 2048 or 4096 bits")
            
            # Generate RSA key using cryptography library
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            key_name = 'ssh-rsa'
        
        elif key_type == 'ecdsa':
            if key_size not in [256, 384, 521]:
                raise ValueError("ECDSA key size must be 256, 384, or 521 bits")
            
            # Map ECDSA key sizes to curves
            curve_map = {
                256: ec.SECP256R1(),
                384: ec.SECP384R1(),
                521: ec.SECP521R1()
            }
            curve = curve_map[key_size]
            
            # Generate ECDSA key
            private_key = ec.generate_private_key(curve)
            key_name = f'ecdsa-sha2-nistp{key_size}'
        
        elif key_type == 'ed25519':
            if key_size != 256:
                raise ValueError("ED25519 only supports 256-bit keys")
            
            # Generate ED25519 key
            private_key = ed25519.Ed25519PrivateKey.generate()
            key_name = 'ssh-ed25519'
        
        else:
            raise ValueError(f"Unsupported key type: {key_type}")
        
        # Serialize public key for SSH format
        public_key_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )
        public_key = public_key_bytes.decode('utf-8')
        
        # Serialize private key
        if passphrase:
            # Encrypt private key with passphrase
            pem_private_key = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode('utf-8'))
            )
        else:
            # Unencrypted private key
            pem_private_key = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        
        # Convert private key to string
        private_key_str = pem_private_key.decode('utf-8')
        
        # Return response with key details
        return {
            'success': True,
            'publicKey': public_key,
            'privateKey': private_key_str,
            'keyType': key_type,
            'keySize': key_size,
            'keyName': key_name
        }
    
    except Exception as e:
        # Comprehensive error logging
        error_details = {
            'success': False,
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc(),
            'python_version': sys.version,
            'platform': sys.platform
        }
        
        # Log error details
        print("SSH Key Generation Error Details:")
        for key, value in error_details.items():
            print(f"{key}: {value}")
        
        return error_details
