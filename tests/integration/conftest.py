import pytest
import time
import requests
import subprocess
import signal
import os
import tempfile
from pathlib import Path

@pytest.fixture(scope="session", autouse=True)
def setup_gpg():
    """Set up GPG for tests"""
    # Create a temporary GNUPGHOME using tempfile
    temp_dir = tempfile.mkdtemp(prefix='gpg_test_')
    temp_gpg_home = Path(temp_dir)
    
    # Set environment variables
    os.environ['GNUPGHOME'] = str(temp_gpg_home)
    
    # Create necessary directories
    os.chmod(temp_gpg_home, 0o700)

    yield

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    """Wait for the API to be ready"""
    max_retries = 30
    retry_interval = 1
    base_url = "http://localhost:5001"

    for _ in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                return
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        time.sleep(retry_interval)

    raise Exception("API failed to start")
