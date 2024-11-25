import os
import sys
import uuid
import traceback

# Ensure proper encoding is set
os.environ['LC_ALL'] = 'en_US.UTF-8'
os.environ['LANG'] = 'en_US.UTF-8'

from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519
from cryptography.hazmat.primitives import serialization

def generate_ssh_key(key_type='rsa', key_size=2048, passphrase=None):
    """Generate an SSH key pair with support for multiple key types"""
    try:
        # Validate and normalize inputs
        key_type = str(key_type).lower()
        key_size = int(key_size)
        
        # Validate key type and size
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
        
        # Determine file paths with explicit encoding
        keys_dir = os.path.join(os.getcwd(), 'keys')
        os.makedirs(keys_dir, exist_ok=True)
        
        # Generate a unique filename
        unique_filename = f'id_{key_type}_{uuid.uuid4().hex[:8]}'
        private_key_path = os.path.join(keys_dir, unique_filename)
        
        # Write private key to file with explicit encoding
        with open(private_key_path, 'wb') as f:
            f.write(pem_private_key)
        
        # Return response with key details
        return {
            'success': True,
            'publicKey': public_key,
            'privateKey': private_key_str,
            'keyType': key_type,
            'keySize': key_size,
            'keyName': key_name,
            'keyPath': private_key_path
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
