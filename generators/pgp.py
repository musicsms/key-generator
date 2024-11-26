import gnupg
import os
from datetime import datetime, timedelta
from utils.response import info_response, error_response

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
    """
    Calculate expiration date based on input string.
    
    Args:
        expire_time (str): Time string like '1y', '2y', 'never'
        
    Returns:
        str: Expiration date in format '2025-12-31' or '0' for never
    """
    if not expire_time or expire_time.lower() == 'never':
        return '0'
        
    try:
        years = int(expire_time.lower().rstrip('y'))
        if years <= 0:
            return '0'
        
        expire_date = datetime.now() + timedelta(days=365 * years)
        return expire_date.strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError("Invalid expiration time format. Use 'Xy' where X is number of years, or 'never'")

def generate_pgp_key(name, email, comment=None, key_type="RSA", key_length=None, curve=None, 
                    passphrase=None, expire_time="2y"):
    """
    Generate a PGP key pair.
    
    Args:
        name (str): Real name of the key owner
        email (str): Email address of the key owner
        comment (str, optional): Optional comment for the key
        key_type (str): Key type ('RSA' or 'ECC')
        key_length (int, optional): Key length for RSA keys
        curve (str, optional): Curve name for ECC keys
        passphrase (str, optional): Optional passphrase for the private key
        expire_time (str, optional): Expiration time ('1y', '2y', 'never'), defaults to '2y'
    
    Returns:
        dict: Response containing the generated keys and status
    """
    try:
        # Input validation
        if not name or not email:
            return error_response("Name and email are required")
        
        if key_type not in KEY_TYPES:
            return error_response(f"Invalid key type. Supported types: {', '.join(KEY_TYPES.keys())}")

        # Handle key configuration based on type
        if key_type == "RSA":
            if not key_length:
                key_length = KEY_TYPES["RSA"]["default_length"]
            if key_length not in KEY_TYPES["RSA"]["valid_lengths"]:
                return error_response(f"Invalid RSA key length. Supported lengths: {KEY_TYPES['RSA']['valid_lengths']}")
            algo_params = {
                'key_type': key_type,
                'key_length': key_length
            }
        else:  # ECC
            if not curve:
                curve = KEY_TYPES["ECC"]["default_curve"]
            if curve not in KEY_TYPES["ECC"]["curves"]:
                return error_response(f"Invalid ECC curve. Supported curves: {KEY_TYPES['ECC']['curves']}")
            algo_params = {
                'key_type': 'ECC',
                'curve': curve
            }

        # Calculate expiration date
        try:
            expire_date = _calculate_expire_date(expire_time)
        except ValueError as e:
            return error_response(str(e))

        # Create gpg home directory if it doesn't exist
        gpg_home = os.path.join(os.getcwd(), 'keys', 'gpg')
        os.makedirs(gpg_home, exist_ok=True)

        # Initialize GPG with cross-platform compatibility
        try:
            # Try newer versions of python-gnupg
            gpg = gnupg.GPG(gnupghome=gpg_home)
        except TypeError:
            # Fall back for older versions
            gpg = gnupg.GPG(homedir=gpg_home)
        
        # Prepare key input
        name_string = name
        if comment:
            name_string = f"{name} ({comment})"
        
        key_input = {
            'name_real': name_string,
            'name_email': email,
            'expire_date': expire_date,
            'key_usage': 'encrypt,sign,auth',
            **algo_params  # Include key type specific parameters
        }

        # Add subkey configuration
        if key_type == "RSA":
            key_input.update({
                'subkey_type': key_type,
                'subkey_length': key_length,
                'subkey_usage': 'encrypt,sign'
            })
        else:
            key_input.update({
                'subkey_type': 'ECC',
                'subkey_curve': curve,
                'subkey_usage': 'encrypt,sign'
            })

        if passphrase:
            key_input['passphrase'] = passphrase

        # Generate key
        key = gpg.gen_key(gpg.gen_key_input(**key_input))
        
        if not key:
            return error_response("Failed to generate PGP key")

        # Export public key
        ascii_armored_public_key = gpg.export_keys(str(key))
        
        # Export private key
        ascii_armored_private_key = gpg.export_keys(
            str(key), 
            secret=True, 
            passphrase=passphrase
        )

        # Create a directory for the key
        key_dir = os.path.join('keys', f"pgp_{email.replace('@', '_at_')}")
        os.makedirs(key_dir, exist_ok=True)

        # Save keys to files
        public_key_path = os.path.join(key_dir, 'public.asc')
        private_key_path = os.path.join(key_dir, 'private.asc')

        with open(public_key_path, 'w') as f:
            f.write(ascii_armored_public_key)
        
        with open(private_key_path, 'w') as f:
            f.write(ascii_armored_private_key)

        # Prepare response data
        response_data = {
            'publicKey': ascii_armored_public_key,
            'privateKey': ascii_armored_private_key,
            'keyId': str(key),
            'keyType': key_type,
            'directory': key_dir,
            'expireDate': expire_date if expire_date != '0' else 'never'
        }

        # Add key type specific details
        if key_type == "RSA":
            response_data['keyLength'] = key_length
        else:
            response_data['curve'] = curve

        return info_response(response_data)

    except Exception as e:
        return error_response(f"Error generating PGP key: {str(e)}")
