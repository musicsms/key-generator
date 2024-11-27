import os
import stat
from pathlib import Path
from utils.sanitize import sanitize_comment

def secure_path_join(*paths):
    """
    Securely join paths, preventing directory traversal attacks.
    """
    # Resolve the absolute path
    base = Path(paths[0]).resolve()
    
    # Join remaining paths
    for p in paths[1:]:
        # Remove any potential directory traversal attempts
        clean_path = Path(p).name
        base = base / clean_path
    
    return str(base)

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
    
    # Sanitize the comment for safe directory creation
    safe_comment = sanitize_comment(comment)
    if not safe_comment:
        raise ValueError("Invalid directory name after sanitization")
    
    # Create the full path securely
    full_path = secure_path_join(base_path, key_type, safe_comment)
    
    # Create directory if it doesn't exist
    os.makedirs(full_path, mode=0o700, exist_ok=True)
    
    # Ensure proper permissions
    os.chmod(full_path, stat.S_IRWXU)
    
    return full_path

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
    # Create secure filenames
    priv_file = secure_path_join(dir_path, f"{key_type}_private.key")
    pub_file = secure_path_join(dir_path, f"{key_type}_public.key")
    
    # Save private key with restricted permissions
    with open(priv_file, 'w') as f:
        os.chmod(priv_file, stat.S_IRUSR | stat.S_IWUSR)  # 0600
        f.write(private_key)
    
    # Save public key
    with open(pub_file, 'w') as f:
        os.chmod(pub_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)  # 0644
        f.write(public_key)
    
    return priv_file, pub_file
