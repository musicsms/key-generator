"""Utility functions for key generation application."""

import os
import logging
from pathlib import Path
from utils.sanitize import validate_comment

logger = logging.getLogger(__name__)


def secure_path_join(base_dir, *paths):
    """
    Securely join one or more path components to the base directory.
    Prevents directory traversal attacks by ensuring the final path
    is within the base directory.

    Args:
        base_dir (str): The base directory to join paths to.
        *paths (str): Additional path components to join.

    Returns:
        str: The securely joined path.

    Raises:
        ValueError: If the resulting path is outside the base directory.
    """
    base_dir = Path(base_dir).resolve()
    final_path = base_dir.joinpath(*paths).resolve()

    if not final_path.is_relative_to(base_dir):
        raise ValueError("Attempted directory traversal attack detected!")

    return str(final_path)


def create_output_directory(key_type, comment):
    """
    Create a directory to store generated keys, ensuring it is secure.

    Args:
        key_type (str): The type of key being generated (e.g., 'ssh', 'rsa').
        comment (str): A comment to include in the directory name.

    Returns:
        str: The path to the created directory.
    """
    try:
        base_path = os.getenv('KEY_STORAGE_PATH', 'keys')
        dir_name = f"{key_type}_{validate_comment(comment)}"
        dir_path = secure_path_join(base_path, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        os.chmod(dir_path, 0o700)
        return dir_path
    except OSError as e:
        logger.error("Failed to create output directory: %s", str(e))
        raise


def save_key_pair(private_key, public_key, directory, key_type):
    """
    Save a generated key pair to files in the specified directory with secure permissions.

    Args:
        private_key (str): The private key to save.
        public_key (str): The public key to save.
        directory (str): The directory to save the keys in.
        key_type (str): The type of key being saved (e.g., 'ssh', 'rsa').

    Returns:
        tuple: Paths to the saved private and public key files.

    Raises:
        ValueError: If input parameters are invalid.
        OSError: If file operations fail.
    """
    if not all([private_key, public_key, directory, key_type]):
        raise ValueError("All parameters must be provided")
    
    if not isinstance(key_type, str) or not key_type.isalnum():
        raise ValueError("Invalid key type format")

    try:
        # Use secure_path_join to prevent directory traversal
        private_path = secure_path_join(directory, f"{key_type}_private.pem")
        public_path = secure_path_join(directory, f"{key_type}_public.pem")

        # Secure file operations with proper permissions
        def write_key_file(path, content, is_private=False):
            flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
            mode = 0o600 if is_private else 0o644
            
            try:
                fd = os.open(path, flags, mode)
                with os.fdopen(fd, 'w') as f:
                    f.write(content)
            except OSError as e:
                logger.error("Failed to write key file %s: %s", path, str(e))
                raise OSError(f"Failed to write key file: {str(e)}")

        write_key_file(private_path, private_key, is_private=True)
        write_key_file(public_path, public_key, is_private=False)

        logger.info("Successfully saved key pair in %s", directory)
        return private_path, public_path

    except OSError as e:
        logger.error("Failed to save key pair: %s", str(e))
        # Clean up any partially written files
        for path in [private_path, public_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError as cleanup_error:
                logger.error("Failed to clean up file %s: %s", path, str(cleanup_error))
        raise


def generate_and_save_key_pair(key_type, key_size, comment, generate_func):
    """
    Generate and save a key pair using the specified generation function.

    Args:
        key_type (str): The type of key to generate (e.g., 'rsa', 'ssh').
        key_size (int): The size of the key.
        comment (str): A comment to include in the key.
        generate_func (callable): The function to call for generating the key pair.

    Returns:
        dict: A dictionary containing the paths to the saved private and public keys.

    Raises:
        ValueError: If input parameters are invalid.
        OSError: If key generation or saving fails.
    """
    try:
        # Generate the key pair
        result = generate_func(key_size=key_size, comment=comment)

        if not result.get('success'):
            raise ValueError('Key generation failed')

        # Create directory and save keys
        dir_path = create_output_directory(key_type, comment)
        private_path, public_path = save_key_pair(
            result['data']['privateKey'],
            result['data']['publicKey'],
            dir_path,
            key_type
        )

        logger.info("%s key pair generated and saved in %s", key_type.upper(), dir_path)
        return {
            'privateKey': private_path,
            'publicKey': public_path
        }

    except (ValueError, OSError) as e:
        logger.error("Failed to generate and save %s key pair: %s", key_type.upper(), str(e))
        raise
