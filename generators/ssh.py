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

def generate_ssh_key(key_type="rsa", key_size=None, comment=None, passphrase=None):
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

        # Set default key sizes
        if key_size is None:
            if key_type == 'rsa':
                key_size = 2048
            elif key_type == 'ecdsa':
                key_size = 256
            elif key_type == 'ed25519':
                key_size = 256

        # Generate key based on type
        if key_type == 'rsa':
            if key_size not in [2048, 4096]:
                return error_response("RSA key size must be 2048 or 4096 bits")
            
            # Generate RSA key using cryptography library
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size
            )
            key_name = 'ssh-rsa'
        
        elif key_type == 'ecdsa':
            if key_size not in [256, 384, 521]:
                return error_response("ECDSA key size must be 256, 384, or 521 bits")
            
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
            # ED25519 has a fixed key size
            private_key = ed25519.Ed25519PrivateKey.generate()
            key_name = 'ssh-ed25519'
        
        # Serialize keys
        if passphrase:
            # For encrypted keys: Use PKCS8 format with PEM encoding
            encryption = serialization.BestAvailableEncryption(passphrase.encode())
            private_key_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption
            )
        else:
            # For unencrypted keys:
            # - RSA keys: Use TraditionalOpenSSL format (which is PKCS1 for RSA)
            # - ED25519 keys: Use OpenSSH format
            # - Other keys: Use TraditionalOpenSSL format
            if key_type == 'ed25519':
                private_key_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.OpenSSH,
                    encryption_algorithm=serialization.NoEncryption()
                )
            else:
                private_key_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
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
            
        # Generate unique directory for key storage
        key_dir = os.path.join(os.environ.get('KEY_STORAGE_PATH', '/tmp'), str(uuid.uuid4()))
        os.makedirs(key_dir, mode=0o700, exist_ok=True)
        
        # Define key paths
        private_path = os.path.join(key_dir, 'id_' + key_type)
        public_path = os.path.join(key_dir, 'id_' + key_type + '.pub')
        
        # Write keys to files
        with open(private_path, 'wb') as f:
            os.chmod(private_path, 0o600)
            f.write(private_key_pem)
            
        with open(public_path, 'w') as f:
            os.chmod(public_path, 0o644)
            f.write(public_key_str)
        
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
