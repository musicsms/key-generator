import os

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
    key_names = {
        'ssh': ('id_rsa', 'id_rsa.pub'),
        'rsa': ('private.pem', 'public.pem'),
        'pgp': ('private.pgp', 'public.pgp')
    }
    
    private_name, public_name = key_names.get(key_type, ('private.key', 'public.key'))
    
    private_path = os.path.join(dir_path, private_name)
    public_path = os.path.join(dir_path, public_name)
    
    with open(private_path, 'w') as f:
        f.write(private_key)
    with open(public_path, 'w') as f:
        f.write(public_key)
