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
    # If no comment provided, use a default name
    if not comment:
        comment = f'default_{key_type}'
    elif len(comment) > 40 or ' ' in comment:
        raise ValueError("Comment must be shorter than 40 characters and not contain spaces")
    
    # Create directory path using just the comment
    dir_path = os.path.join('keys', comment)
    
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
    """
    # Generate a unique identifier
    unique_id = uuid.uuid4().hex[:8]
    
    # Define file extensions based on key type
    extensions = {
        'ssh': ('.pem', '.pub'),
        'rsa': ('.pem', '.pub'),
        'pgp': ('.pgp', '.pub.pgp')
    }
    
    priv_ext, pub_ext = extensions.get(key_type, ('.key', '.pub'))
    
    # Create unique filenames
    base_name = f"{key_type}_{unique_id}"
    private_name = f"{base_name}{priv_ext}"
    public_name = f"{base_name}{pub_ext}"
    
    private_path = os.path.join(dir_path, private_name)
    public_path = os.path.join(dir_path, public_name)
    
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
