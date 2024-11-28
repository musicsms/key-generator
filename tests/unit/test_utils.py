import pytest
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.utils import create_output_directory, save_key_pair
from utils.sanitize import validate_comment, sanitize_comment
from utils.response import info_response, error_response

def test_validate_comment():
    """Test comment validation"""
    # Valid comments
    assert validate_comment("test_key") == "test_key"
    assert validate_comment("my-key-2023") == "my-key-2023"
    assert validate_comment("key_123") == "key_123"
    
    # Invalid comments
    assert validate_comment("test key") == "test_key"  # Spaces are replaced with underscores
    assert validate_comment("key@invalid") == "keyinvalid"  # Special chars are removed
    assert validate_comment("") == ""  # Empty string returns empty string

def test_create_output_directory(tmp_path):
    """Test output directory creation"""
    key_type = "ssh"
    comment = "test_key"
    dir_path = create_output_directory(key_type, comment)
    
    assert os.path.exists(dir_path)
    assert os.path.isdir(dir_path)
    assert os.stat(dir_path).st_mode & 0o777 == 0o700  # Check permissions

def test_save_key_pair(tmp_path):
    """Test key pair saving"""
    private_key = "test private key"
    public_key = "test public key"
    key_type = "ssh"
    dir_path = create_output_directory(key_type)
    
    private_path, public_path = save_key_pair(
        private_key, public_key,
        dir_path, key_type
    )
    
    assert os.path.exists(private_path)
    assert os.path.exists(public_path)
    
    # Check file contents
    with open(private_path) as f:
        assert f.read() == private_key
    with open(public_path) as f:
        assert f.read() == public_key
    
    # Check file permissions
    assert os.stat(private_path).st_mode & 0o777 == 0o600
    assert os.stat(public_path).st_mode & 0o777 == 0o644

def test_info_response():
    """Test successful response formatting"""
    data = {"key": "value"}
    response = info_response(data)
    
    assert response["success"] is True
    assert response["data"]["key"] == "value"

def test_error_response():
    """Test error response formatting"""
    message = "Test error"
    status_code = 500
    response = error_response(message, status_code)
    
    assert response["success"] is False
    assert response["error_message"] == message
