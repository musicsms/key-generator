import os
import uuid

def create_output_directory(key_type, comment=''):
    """Create and return a directory path for storing generated keys
    
    Args:
        key_type (str): Type of key ('ssh', 'rsa', 'pgp')
        comment (str): Optional comment for naming the directory
    
    Returns:
        str: Path to the created directory
    
    Raises:
        ValueError: If key_type or comment contains invalid characters
    """
    # Validate key type
    valid_key_types = {'ssh', 'rsa', 'pgp'}
    if key_type not in valid_key_types:
        raise ValueError("Invalid key type")
    
    # If no comment provided, use a default name
    if not comment:
        comment = f'default_{key_type}'
    
    # Validate comment length and characters
    if len(comment) > 40:
        raise ValueError("Comment must be shorter than 40 characters")
    
    # Only allow alphanumeric characters, underscores, and hyphens
    if not all(c.isalnum() or c in '_-' for c in comment):
        raise ValueError("Comment can only contain letters, numbers, underscores, and hyphens")
    
    # Get the absolute path to the keys directory
    keys_dir = os.path.abspath('keys')
    
    # Create the full directory path and normalize it
    dir_path = os.path.normpath(os.path.join(keys_dir, comment))
    
    # Verify the normalized path is still under the keys directory
    if not dir_path.startswith(keys_dir):
        raise ValueError("Invalid directory path")
    
    # Create directory if it doesn't exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    return dir_path

def save_key_pair(private_key, public_key, dir_path, key_type):
    """Save key pair to files in the specified directory
    
    Args:
        private_key (str): Private key content
        public_key (str): Public key content
        dir_path (str): Directory to save the keys
        key_type (str): Type of key ('ssh', 'rsa', 'pgp')
    
    Raises:
        ValueError: If key_type is invalid or dir_path is outside keys directory
    """
    # Validate key type
    valid_key_types = {'ssh', 'rsa', 'pgp'}
    if key_type not in valid_key_types:
        raise ValueError("Invalid key type")
    
    # Get the absolute path to the keys directory
    keys_dir = os.path.abspath('keys')
    
    # Normalize the directory path
    dir_path = os.path.normpath(os.path.abspath(dir_path))
    
    # Verify the directory path is under the keys directory
    if not dir_path.startswith(keys_dir):
        raise ValueError("Invalid directory path")
    
    # Generate a unique identifier
    unique_id = uuid.uuid4().hex[:8]
    
    # Define file extensions based on key type
    extensions = {
        'ssh': ('.pem', '.pub'),
        'rsa': ('.pem', '.pub'),
        'pgp': ('.pgp', '.pub.pgp')
    }
    
    priv_ext, pub_ext = extensions[key_type]
    
    # Create unique filenames
    base_name = f"{key_type}_{unique_id}"
    private_name = f"{base_name}{priv_ext}"
    public_name = f"{base_name}{pub_ext}"
    
    # Create absolute paths and verify they are under the keys directory
    private_path = os.path.normpath(os.path.join(dir_path, private_name))
    public_path = os.path.normpath(os.path.join(dir_path, public_name))
    
    if not all(p.startswith(keys_dir) for p in [private_path, public_path]):
        raise ValueError("Invalid file paths")
    
    # Ensure directory exists
    os.makedirs(dir_path, exist_ok=True)
    
    # Save private key with restricted permissions
    with open(private_path, 'w') as f:
        os.chmod(private_path, 0o600)  # Set file permissions to owner read/write only
        f.write(private_key)
    
    # Save public key
    with open(public_path, 'w') as f:
        os.chmod(public_path, 0o644)  # Set file permissions to owner read/write, others read
        f.write(public_key)
    
    return private_path, public_path
