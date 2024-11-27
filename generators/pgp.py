import os
import gnupg
from datetime import datetime, timedelta
import re
from utils.response import info_response, error_response
from utils.sanitize import validate_comment
from utils.utils import create_output_directory, save_key_pair
from subprocess import run, CalledProcessError, PIPE
from typing import Tuple, Optional
import shutil

# Key type configurations
KEY_TYPES = {
    "RSA": {
        "type": "RSA",
        "allowed_lengths": [2048, 3072, 4096],
        "default_length": 2048
    },
    "ECC": {
        "type": "ECC",
        "allowed_curves": ["secp256k1", "secp384r1", "secp521r1", "brainpoolP256r1", "brainpoolP384r1", "brainpoolP512r1"],
        "default_curve": "secp256k1"
    }
}

def _calculate_expire_date(expire_time):
    """Calculate expiration date from input string"""
    if expire_time.lower() == 'never':
        return '0'
    
    try:
        years = int(expire_time.lower().rstrip('y'))
        if years <= 0:
            return '0'
        
        expire_date = datetime.now() + timedelta(days=365 * years)
        return expire_date.strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid expiration time format. Use 'Xy' where X is number of years, or 'never'")

def _get_gpg_binary() -> Tuple[Optional[str], Optional[str]]:
    """
    Get the full path to the GPG binary.
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (path to gpg binary if found, error message if not found)
    """
    # List of common GPG binary names and locations
    gpg_paths = [
        '/usr/bin/gpg',
        '/usr/local/bin/gpg',
        '/opt/homebrew/bin/gpg',
        'C:\\Program Files (x86)\\GnuPG\\bin\\gpg.exe',
        'C:\\Program Files\\GnuPG\\bin\\gpg.exe'
    ]
    
    # First try the PATH
    gpg_command = shutil.which('gpg')
    if gpg_command:
        try:
            result = run([gpg_command, '--version'], 
                        capture_output=True, 
                        text=True, 
                        check=True,
                        timeout=5)  # Add timeout for safety
            if result.returncode == 0:
                return gpg_command, None
        except (CalledProcessError, OSError):
            pass

    # Then try known locations
    for path in gpg_paths:
        if os.path.isfile(path):
            try:
                result = run([path, '--version'], 
                           capture_output=True, 
                           text=True, 
                           check=True,
                           timeout=5)  # Add timeout for safety
                if result.returncode == 0:
                    return path, None
            except (CalledProcessError, OSError):
                continue

    return None, "GPG binary not found in system"

def check_gpg_available() -> Tuple[bool, Optional[str]]:
    """
    Check if GPG is available on the system.
    
    Returns:
        Tuple[bool, Optional[str]]: (True if GPG is available, error message if not)
    """
    gpg_path, error = _get_gpg_binary()
    if gpg_path:
        return True, None
    return False, error or "GPG is not installed or not accessible"

def _process_expiration_time(expire_time):
    if expire_time.lower() == 'never':
        return '0'
    
    try:
        years = int(expire_time.lower().rstrip('y'))
        if years <= 0:
            return '0'
        
        expire_date = datetime.now() + timedelta(days=365 * years)
        return expire_date.strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid expiration time format. Use 'Xy' where X is number of years, or 'never'")

def _generate_key_params(name, email, comment, key_type, key_length, curve, passphrase, expiration):
    params = f"Key-Type: {key_type}\n"
    params += f"Key-Length: {key_length}\n" if key_type == "RSA" else f"Key-Curve: {curve}\n"
    params += f"Name-Real: {name}\n"
    params += f"Name-Comment: {comment}\n" if comment else ""
    params += f"Name-Email: {email}\n"
    params += f"Expire-Date: {expiration}\n"
    params += f"Passphrase: {passphrase}\n" if passphrase else ""
    params += "%commit\n"
    return params

def generate_pgp_key(name, email, comment=None, key_type="RSA", key_length=None, curve=None, 
                    passphrase=None, expire_time="2y"):
    """
    Generate a PGP key pair with the given parameters.
    
    Args:
        name (str): Name for the key
        email (str): Email for the key
        comment (str, optional): Comment for the key. Defaults to None.
        key_type (str, optional): Type of key ('RSA' or 'ECC'). Defaults to "RSA".
        key_length (int, optional): Key length for RSA keys. Defaults to None.
        curve (str, optional): Curve name for ECC keys. Defaults to None.
        passphrase (str, optional): Passphrase for the key. Defaults to None.
        expire_time (str, optional): Expiration time in format 'Xy' or 'never'. Defaults to "2y".
    
    Returns:
        dict: Response containing the generated keys or error message
    """
    try:
        # Get GPG binary path
        gpg_path, error = _get_gpg_binary()
        if not gpg_path:
            return error_response(error or "GPG is not installed or not accessible")

        # Validate inputs
        if not name or not email:
            return error_response("Name and email are required")
        
        if comment:
            comment = validate_comment(comment)
        
        # Validate key type and parameters
        key_type = key_type.upper()
        if key_type not in KEY_TYPES:
            return error_response(f"Invalid key type. Supported types: {', '.join(KEY_TYPES.keys())}")
        
        key_config = KEY_TYPES[key_type]
        
        if key_type == "RSA":
            if not key_length:
                key_length = key_config["default_length"]
            elif key_length not in key_config["allowed_lengths"]:
                return error_response(f"Invalid key length for {key_type}. Allowed lengths: {key_config['allowed_lengths']}")
        elif key_type == "ECC":
            if not curve:
                curve = key_config["default_curve"]
            elif curve not in key_config["allowed_curves"]:
                return error_response(f"Invalid curve for {key_type}. Allowed curves: {key_config['allowed_curves']}")

        # Process expiration time
        try:
            expiration = _process_expiration_time(expire_time)
        except ValueError as e:
            return error_response(str(e))

        # Generate key
        try:
            result = run([gpg_path, '--batch', '--gen-key'], 
                        input=_generate_key_params(name, email, comment, key_type, key_length, curve, passphrase, expiration),
                        text=True,
                        capture_output=True,
                        check=True,
                        timeout=30)  # Add reasonable timeout
            
            if result.returncode != 0:
                return error_response(f"Key generation failed: {result.stderr}")
                
            # Export the keys
            public_key = run([gpg_path, '--armor', '--export', email],
                           capture_output=True,
                           text=True,
                           check=True,
                           timeout=10).stdout
                           
            private_key = run([gpg_path, '--armor', '--export-secret-key', email],
                            capture_output=True,
                            text=True,
                            check=True,
                            timeout=10).stdout
            
            if not public_key or not private_key:
                return error_response("Failed to export generated keys")
            
            # Save keys to files
            key_files = save_key_pair(public_key, private_key, "pgp")
            
            return info_response({
                "publicKey": public_key,
                "privateKey": private_key,
                "publicKeyFile": key_files["public"],
                "privateKeyFile": key_files["private"]
            })
            
        except CalledProcessError as e:
            return error_response(f"GPG command failed: {e.stderr}")
        except TimeoutError:
            return error_response("GPG operation timed out")
        except Exception as e:
            return error_response(f"Error generating PGP key: {str(e)}")
            
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}")
