import os
import uuid

def create_output_directory(key_type, comment=''):
    """Create and return a directory path for storing generated keys
    
    Args:
        key_type (str): Type of key ('ssh', 'rsa', 'pgp')
        comment (str): Optional comment for naming the directory
    
    Returns:
        str: Path to the created directory
    """
    # Get the base storage path from environment or use default
    base_path = os.getenv('KEY_STORAGE_PATH', 'keys')
    
    # Validate key_type
    if key_type not in ['ssh', 'rsa', 'pgp']:
        raise ValueError("Invalid key type. Must be one of: ssh, rsa, pgp")
    
    # If no comment provided, use a UUID
    if not comment:
        comment = str(uuid.uuid4())
    elif len(comment) > 40 or ' ' in comment:
        raise ValueError("Comment must be shorter than 40 characters and not contain spaces")
    
    # Create directory path using key type subfolder
    dir_path = os.path.join(base_path, key_type, comment)
    
    # Create directory if it doesn't exist
    os.makedirs(dir_path, exist_ok=True)
    
    # Set proper permissions for the directory
    os.chmod(dir_path, 0o700)
    
    return dir_path

def save_key_pair(private_key, public_key, dir_path, key_type):
    """Save key pair to files in the specified directory
    
    Args:
        private_key (str): Private key content
        public_key (str): Public key content
        dir_path (str): Directory to save the keys in
        key_type (str): Type of key ('ssh', 'rsa', 'pgp')
    
    Returns:
        tuple: (private_key_path, public_key_path)
    """
    # Create unique filenames
    key_id = str(uuid.uuid4())[:8]
    private_key_path = os.path.join(dir_path, f'{key_id}.private')
    public_key_path = os.path.join(dir_path, f'{key_id}.public')
    
    # Save private key with restricted permissions
    with open(private_key_path, 'w') as f:
        f.write(private_key)
    os.chmod(private_key_path, 0o600)
    
    # Save public key
    with open(public_key_path, 'w') as f:
        f.write(public_key)
    os.chmod(public_key_path, 0o644)
    
    return private_key_path, public_key_path
