import os
import pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables before each test"""
    # Set up test directories
    test_dir = Path(__file__).parent / 'test_keys'
    test_dir.mkdir(exist_ok=True)
    for key_type in ['ssh', 'rsa', 'pgp']:
        (test_dir / key_type).mkdir(exist_ok=True)
    (test_dir / '.gnupg').mkdir(exist_ok=True)
    
    # Set environment variables
    os.environ['KEY_STORAGE_PATH'] = str(test_dir)
    os.environ['GNUPGHOME'] = str(test_dir / '.gnupg')
    
    # Set proper permissions
    for path in test_dir.rglob('*'):
        if path.is_dir():
            path.chmod(0o700)
    
    yield
    
    # Clean up (optional, comment out if you want to inspect files after tests)
    # import shutil
    # shutil.rmtree(test_dir, ignore_errors=True)
