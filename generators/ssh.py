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
from cryptography.hazmat.primitives.asymmetric.ec import SECP384R1
from cryptography.hazmat.primitives import serialization

def generate_ssh_key(key_type="ed25519", key_size=None, comment=None, passphrase=None):
    """
    Generate an SSH key pair.
    
    Args:
        key_type (str): Type of key to generate (rsa, ecdsa, ed25519)
        key_size (int, optional): Key size for RSA/ECDSA keys (not used for ed25519)
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

        # Set encryption algorithm if passphrase is provided
        encryption = serialization.BestAvailableEncryption(passphrase.encode()) if passphrase else serialization.NoEncryption()
        
        if key_type == 'rsa':
            # Enforce minimum RSA key size of 3072 bits
            if not key_size or key_size < 3072:
                key_size = 4096
            
            # Generate RSA key using cryptography library
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            key_name = 'ssh-rsa'
        
        elif key_type == 'ecdsa':
            # Use SECP384R1 curve for ECDSA (NIST P-384)
            private_key = ec.generate_private_key(SECP384R1())
            key_name = 'ecdsa-sha2-nistp384'
        
        elif key_type == 'ed25519':
            # Ed25519 has fixed key size and is recommended
            private_key = ed25519.Ed25519PrivateKey.generate()
            key_name = 'ssh-ed25519'
        
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
        
        return info_response({
            'privateKey': private_key_pem.decode(),
            'publicKey': public_key_str,
            'keyType': key_type,
            'keySize': key_size,
            'comment': comment
        })
        
    except Exception as e:
        print("SSH Key Generation Error Details:")
        print(f"success: False")
        print(f"error_type: {type(e).__name__}")
        print(f"error_message: {str(e)}")
        print(f"traceback: {traceback.format_exc()}")
        print(f"python_version: {sys.version}")
        print(f"platform: {sys.platform}")
        return error_response(str(e))
