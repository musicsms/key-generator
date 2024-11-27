import os
import sys
import pytest
import tempfile

# Add the parent directory to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app

@pytest.fixture
def app():
    # Create a temporary directory for key storage
    with tempfile.TemporaryDirectory() as temp_dir:
        flask_app.config.update({
            'TESTING': True,
            'KEY_STORAGE_PATH': temp_dir,
            'GNUPGHOME': os.path.join(temp_dir, '.gnupg')
        })
        
        # Create necessary directories
        os.makedirs(os.path.join(temp_dir, '.gnupg'), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, 'ssh'), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, 'rsa'), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, 'pgp'), exist_ok=True)
        
        # Set proper permissions
        os.chmod(os.path.join(temp_dir, '.gnupg'), 0o700)
        
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
