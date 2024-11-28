import os
import gnupg
from datetime import datetime, timedelta
import re
from utils.response import info_response, error_response
from utils.sanitize import validate_comment
from utils.utils import create_output_directory, save_key_pair
# Subprocess is required for GPG operations and is used securely with input validation
# nosec B404 - subprocess is necessary for GPG operations
from subprocess import run, CalledProcessError
import shutil
import uuid
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Key type configurations
KEY_TYPES = {
    "RSA": {
        "type": "RSA",
        "valid_lengths": [2048, 3072, 4096],
        "default_length": 2048
    },
    "ECC": {
        "type": "ECC",
        "curves": ["secp256k1", "secp384r1", "secp521r1", "brainpoolP256r1", "brainpoolP384r1", "brainpoolP512r1"],
        "default_curve": "secp256k1"
    }
}

def _calculate_expire_date(expire_time):
    """Calculate expiration date from input string"""
    if expire_time.lower() == 'never':
        return '0'
    
    try:
        # Handle days format (e.g., '1d')
        if expire_time.lower().endswith('d'):
            days = int(expire_time.lower().rstrip('d'))
            if days <= 0:
                return '0'
            expire_date = datetime.now() + timedelta(days=days)
            return expire_date.strftime('%Y-%m-%d')
            
        # Handle years format (e.g., '1y')
        if expire_time.lower().endswith('y'):
            years = int(expire_time.lower().rstrip('y'))
            if years <= 0:
                return '0'
            expire_date = datetime.now() + timedelta(days=365 * years)
            return expire_date.strftime('%Y-%m-%d')
            
        raise ValueError("Invalid expiration time format")
    except ValueError:
        raise ValueError("Invalid expiration time format. Use 'Xd' for days, 'Xy' for years, or 'never'")

def _get_gpg_path():
    """Get the full path to the GPG executable."""
    gpg_path = shutil.which('gpg')
    if not gpg_path:
        return None
    return gpg_path

def _check_gpg_installation():
    """
    Check if GPG is installed and accessible.
    Returns:
        tuple: (bool, str) - (is_installed, error_message)
    """
    try:
        gpg_path = _get_gpg_path()
        if not gpg_path:
            return False, "GPG is not installed or not in PATH"
            
        # Use the full path to GPG with input validation
        # nosec B603 - we are using a validated full path from shutil.which()
        result = run([gpg_path, '--version'], 
            capture_output=True, 
            text=True, 
            check=True)
        return True, None
            
    except CalledProcessError as e:
        return False, f"Error checking GPG: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error checking GPG: {str(e)}"

def _sanitize_name(name: str) -> str:
    """
    Sanitize and validate name input.
    
    Args:
        name (str): Input name to sanitize
    
    Returns:
        str: Sanitized name
    
    Raises:
        ValueError: If name is invalid
    """
    if not name or not isinstance(name, str):
        raise ValueError("Name must be a non-empty string")
    
    # Remove any potentially dangerous characters
    sanitized_name = re.sub(r'[<>&\'"()]', '', name).strip()
    
    if not sanitized_name:
        raise ValueError("Invalid name after sanitization")
    
    # Limit name length
    return sanitized_name[:100]

def _sanitize_email(email: str) -> str:
    """
    Sanitize and validate email input.
    
    Args:
        email (str): Input email to validate
    
    Returns:
        str: Validated email
    
    Raises:
        ValueError: If email is invalid
    """
    if not email or not isinstance(email, str):
        raise ValueError("Email must be a non-empty string")
    
    email = email.strip()
    
    if not EMAIL_REGEX.match(email):
        raise ValueError("Invalid email format")
    
    return email

def _sanitize_comment(comment: Optional[str]) -> Optional[str]:
    """
    Sanitize and validate comment input.
    
    Args:
        comment (str, optional): Input comment to sanitize
    
    Returns:
        str or None: Sanitized comment
    """
    if not comment or not isinstance(comment, str):
        return None
    
    # Remove potentially dangerous characters
    sanitized_comment = re.sub(r'[<>&\'"()]', ' ', comment).strip()
    
    # Limit comment length
    return sanitized_comment[:100] or None

def generate_pgp_key(
    name: str, 
    email: str, 
    comment: Optional[str] = None, 
    key_type: str = "RSA", 
    key_length: Optional[int] = None, 
    curve: Optional[str] = None, 
    passphrase: Optional[str] = None, 
    expire_time: str = "never"
):
    """
    Generate a PGP key pair with enhanced security and validation.
    """
    try:
        # Validate and sanitize inputs
        try:
            name = _sanitize_name(name)
            email = _sanitize_email(email)
            comment = _sanitize_comment(comment)
        except ValueError as e:
            logger.error(f"Input validation error: {str(e)}")
            return error_response(str(e))
        
        # Ensure a passphrase is provided for key export
        if not passphrase:
            passphrase = str(uuid.uuid4())  # Generate a random passphrase
        
        # Get GPG path
        gpg_path = _get_gpg_path()
        if not gpg_path:
            logger.error("GPG is not installed or not in PATH")
            return error_response("GPG is not installed or not in PATH")
            
        # Check GPG installation
        gpg_ok, error_msg = _check_gpg_installation()
        if not gpg_ok:
            logger.error(f"GPG installation check failed: {error_msg}")
            return error_response(error_msg)

        # Validate key type
        key_type = key_type.upper()
        if key_type not in ["RSA", "ECC"]:
            logger.error(f"Invalid key type: {key_type}")
            return error_response("Invalid key type. Must be 'RSA' or 'ECC'")

        # Validate and set key length for RSA
        if key_type == "RSA":
            if not key_length:
                key_length = 2048
            if key_length not in [2048, 3072, 4096]:
                logger.error(f"Invalid RSA key length: {key_length}")
                return error_response("Invalid key length for RSA. Must be 2048, 3072, or 4096")

        # Validate curve for ECC
        if key_type == "ECC":
            if not curve:
                curve = "secp256k1"
            valid_curves = ["secp256k1", "secp384r1", "secp521r1", "brainpoolP256r1", "brainpoolP384r1", "brainpoolP512r1"]
            if curve not in valid_curves:
                logger.error(f"Invalid ECC curve: {curve}")
                return error_response(f"Invalid curve. Must be one of: {', '.join(valid_curves)}")

        try:
            expire_date = _calculate_expire_date(expire_time)
        except ValueError as e:
            logger.error(f"Invalid expiration time: {expire_time}")
            return error_response(str(e))

        # Create gpg home directory if it doesn't exist
        gpg_home = os.environ.get('GNUPGHOME', os.path.join(os.getcwd(), 'keys', 'gpg'))
        os.makedirs(gpg_home, mode=0o700, exist_ok=True)  # Use 700 permissions to restrict access

        # Initialize GPG with cross-platform compatibility
        try:
            # Try newer versions of python-gnupg
            gpg = gnupg.GPG(gnupghome=gpg_home, gpgbinary=gpg_path)
        except TypeError:
            # Fall back for older versions
            gpg = gnupg.GPG(homedir=gpg_home, gpgbinary=gpg_path)
            
        # Try to list keys to verify GPG is working
        try:
            gpg.list_keys()
        except Exception as e:
            logger.error(f"GPG key listing failed: {str(e)}")
            error_msg = str(e).lower()
            if "not installed" in error_msg or "cannot run" in error_msg:
                gpg_installed, error_message = _check_gpg_installation()
                if not gpg_installed:
                    return error_response(error_message)
            return error_response(f"GPG error: {str(e)}")

        # Prepare key input string
        name_string = name
        if comment:
            name_string = f"{name} ({comment})"
        
        # Create key input string in the format expected by GPG
        logger.debug(f"Generating key with params: name={name_string}, email={email}, key_type={key_type}")
        key_input = gpg.gen_key_input(
            name_real=name_string,
            name_email=email,
            expire_date=expire_date,
            key_type='RSA' if key_type == 'RSA' else 'DSA',
            key_length=key_length if key_type == 'RSA' else 2048,
            subkey_type='RSA',
            subkey_length=key_length if key_type == 'RSA' else 2048,
            passphrase=passphrase
        )

        # Generate key
        try:
            key = gpg.gen_key(key_input)
        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            return error_response(f"Failed to generate PGP key: {str(e)}")
        
        if not key:
            logger.error("Key generation returned empty result")
            return error_response("Failed to generate PGP key")

        # Export public key
        try:
            ascii_armored_public_key = gpg.export_keys(str(key))
        except Exception as e:
            logger.error(f"Public key export failed: {str(e)}")
            return error_response(f"Failed to export public key: {str(e)}")
        
        # Export private key
        try:
            ascii_armored_private_key = gpg.export_keys(
                str(key), 
                secret=True, 
                passphrase=passphrase
            )
        except Exception as e:
            logger.error(f"Private key export failed: {str(e)}")
            return error_response(f"Failed to export private key: {str(e)}")

        if not ascii_armored_public_key or not ascii_armored_private_key:
            logger.error("Exported keys are empty")
            return error_response("Failed to export generated keys")

        # Create a directory for the key using a modified directory name
        safe_comment = re.sub(r'\W+', '_', comment) if comment else ''
        key_dir = create_output_directory('pgp', safe_comment or email.replace('@', '_at_'))

        # Save keys using save_key_pair
        private_path, public_path = save_key_pair(
            ascii_armored_private_key,
            ascii_armored_public_key,
            key_dir,
            'pgp'
        )

        # Prepare response data
        response_data = {
            'publicKey': ascii_armored_public_key,
            'privateKey': ascii_armored_private_key,
            'keyId': str(key),
            'keyType': key_type,
            'keyLength': key_length if key_type == 'RSA' else None,
            'curve': curve if key_type == 'ECC' else None,
            'name': name,
            'email': email,
            'comment': comment,
            'expireDate': expire_date
        }

        return info_response(response_data)

    except Exception as e:
        logger.error(f"Unexpected error generating PGP key: {str(e)}", exc_info=True)
        return error_response(f"Error generating PGP key: {str(e)}")
