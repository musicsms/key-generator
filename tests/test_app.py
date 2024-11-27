import os
import sys
import pytest
from flask import url_for

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
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Key Generator' in rv.data

def test_health_check(client):
    """Test health check endpoint"""
    rv = client.get('/health')
    assert rv.status_code == 200
    assert rv.json['status'] == 'healthy'

def test_generate_ssh_key(client):
    """Test SSH key generation endpoint"""
    data = {
        'key_type': 'rsa',
        'key_size': 2048,
        'comment': 'test@example.com'
    }
    rv = client.post('/generate/ssh', json=data)
    assert rv.status_code == 200
    assert 'private_key' in rv.json
    assert 'public_key' in rv.json

def test_generate_rsa_key(client):
    """Test RSA key generation endpoint"""
    data = {
        'key_size': 2048,
        'passphrase': 'test123'
    }
    rv = client.post('/generate/rsa', json=data)
    assert rv.status_code == 200
    assert 'private_key' in rv.json
    assert 'public_key' in rv.json
