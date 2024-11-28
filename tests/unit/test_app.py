import pytest
import json
import os
import tempfile
import stat
from pathlib import Path
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def gpg_home():
    """Create a temporary GPG home directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        old_gnupghome = os.environ.get('GNUPGHOME')
        # Set proper permissions for GPG home
        os.chmod(temp_dir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)  # 700
        os.environ['GNUPGHOME'] = temp_dir
        
        # Initialize GPG home directory
        os.makedirs(os.path.join(temp_dir, 'private-keys-v1.d'), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, 'openpgp-revocs.d'), exist_ok=True)
        
        # Create required files
        Path(os.path.join(temp_dir, 'gpg.conf')).touch()
        Path(os.path.join(temp_dir, 'trustdb.gpg')).touch()
        
        yield temp_dir
        
        if old_gnupghome:
            os.environ['GNUPGHOME'] = old_gnupghome
        else:
            del os.environ['GNUPGHOME']

def test_index(client):
    """Test index page loads"""
    response = client.get('/')
    assert response.status_code == 200

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_generate_passphrase(client):
    """Test passphrase generation endpoint"""
    response = client.post('/generate/passphrase',
                         json={'length': 16})
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert isinstance(data['data']['passphrase'], str)
    assert len(data['data']['passphrase']) == 16

def test_generate_ssh(client):
    """Test SSH key generation endpoint"""
    response = client.post('/generate/ssh',
                         json={'keyType': 'rsa', 'comment': 'test'})
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert data['data']['privateKey'].startswith('-----BEGIN')
    assert data['data']['publicKey'].startswith('ssh-rsa')
    assert 'directory' in data['data']
    assert 'privatePath' in data['data']
    assert 'publicPath' in data['data']

def test_generate_rsa(client):
    """Test RSA key generation endpoint"""
    response = client.post('/generate/rsa',
                         json={'keySize': 2048, 'comment': 'test'})
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert data['data']['privateKey'].startswith('-----BEGIN')
    assert data['data']['publicKey'].startswith('-----BEGIN PUBLIC KEY-----')
    assert data['data']['keySize'] == 2048
    assert 'directory' in data['data']
    assert 'privatePath' in data['data']
    assert 'publicPath' in data['data']

def test_generate_pgp(client, gpg_home):
    """Test PGP key generation endpoint"""
    response = client.post('/generate/pgp',
                         json={
                             'name': 'Test User',
                             'email': 'test@example.com',
                             'keyType': 'RSA',
                             'keyLength': 2048,
                             'expireTime': '2y',
                             'passphrase': 'test123'
                         })
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert data['data']['privateKey'].startswith('-----BEGIN PGP PRIVATE KEY BLOCK-----')
    assert data['data']['publicKey'].startswith('-----BEGIN PGP PUBLIC KEY BLOCK-----')
    assert data['data']['keyType'] == 'RSA'
    assert data['data']['keyLength'] == 2048

def test_invalid_input(client, gpg_home):
    """Test error handling for invalid input"""
    # Test invalid passphrase length
    response = client.post('/generate/passphrase',
                         json={'length': -1})
    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'error_message' in response.json

    # Test invalid SSH key type
    response = client.post('/generate/ssh',
                         json={'keyType': 'invalid'})
    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'error_message' in response.json

    # Test invalid RSA key size
    response = client.post('/generate/rsa',
                         json={'keySize': 1024})
    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'error_message' in response.json

    # Test invalid PGP parameters
    response = client.post('/generate/pgp',
                         json={'name': '', 'email': 'invalid'})
    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'error_message' in response.json
