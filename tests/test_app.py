import os
import sys
import pytest
from flask import url_for
from generators import ssh, rsa

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test that home page loads successfully"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Key Generator' in response.data

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

@pytest.mark.parametrize('key_type', ['rsa', 'ed25519', 'ecdsa'])
def test_generate_ssh_key(client, key_type):
    """Test SSH key generation endpoint with different key types"""
    data = {
        'key_type': key_type,
        'key_size': 2048 if key_type == 'rsa' else None,
        'comment': 'test@example.com'
    }
    response = client.post('/generate/ssh', json=data)
    assert response.status_code == 200
    result = response.json
    assert 'success' in result
    assert result['success'] == True
    assert 'data' in result
    result_data = result['data']
    assert 'privateKey' in result_data
    assert 'publicKey' in result_data
    assert isinstance(result_data['privateKey'], str)
    assert isinstance(result_data['publicKey'], str)
    assert result_data['publicKey'].startswith('ssh-')

@pytest.mark.parametrize('key_size', [2048, 4096])
def test_generate_rsa_key(client, key_size):
    """Test RSA key generation endpoint with different key sizes"""
    data = {
        'key_size': key_size,
        'passphrase': 'test123'
    }
    response = client.post('/generate/rsa', json=data)
    assert response.status_code == 200
    result = response.json
    assert 'success' in result
    assert result['success'] == True
    assert 'data' in result
    result_data = result['data']
    assert 'privateKey' in result_data
    assert 'publicKey' in result_data
    assert isinstance(result_data['privateKey'], str)
    assert isinstance(result_data['publicKey'], str)
    assert '-----BEGIN PUBLIC KEY-----' in result_data['publicKey']
    assert '-----BEGIN ENCRYPTED PRIVATE KEY-----' in result_data['privateKey']

def test_invalid_ssh_key_type(client):
    """Test error handling for invalid SSH key type"""
    data = {
        'keyType': 'invalid',
        'comment': 'test@example.com'
    }
    response = client.post('/generate/ssh', json=data)
    assert response.status_code == 400
    result = response.json
    assert 'success' in result
    assert result['success'] == False
    assert 'error_message' in result

def test_invalid_rsa_key_size(client):
    """Test error handling for invalid RSA key size"""
    data = {
        'keySize': 1024,  # Too small
        'passphrase': 'test123'
    }
    response = client.post('/generate/rsa', json=data)
    assert response.status_code == 400
    result = response.json
    assert 'success' in result
    assert result['success'] == False
    assert 'error_message' in result
