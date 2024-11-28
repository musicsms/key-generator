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
    os.environ['FLASK_DEBUG'] = '0'
    
    # Set proper permissions
    for path in test_dir.rglob('*'):
        if path.is_dir():
            os.chmod(path, 0o700)
    
    yield
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
