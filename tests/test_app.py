import pytest
import json
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'healthy'}

def test_passphrase_generation(client):
    # Test default parameters
    response = client.post('/generate/passphrase',
                         data=json.dumps({}),
                         content_type='application/json')
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert len(data['data']['passphrase']) == 16

    # Test custom parameters
    response = client.post('/generate/passphrase',
                         data=json.dumps({
                             'length': 20,
                             'includeNumbers': True,
                             'includeSpecial': False,
                             'excludeChars': '0o1l'
                         }),
                         content_type='application/json')
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert len(data['data']['passphrase']) == 20
    assert not any(c in data['data']['passphrase'] for c in '0o1l')

def test_ssh_key_generation(client):
    response = client.post('/generate/ssh',
                         data=json.dumps({
                             'keyType': 'ed25519',
                             'passphrase': 'test123'
                         }),
                         content_type='application/json')
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert 'privateKey' in data['data']
    assert 'publicKey' in data['data']

def test_rsa_key_generation(client):
    response = client.post('/generate/rsa',
                         data=json.dumps({
                             'keySize': 2048,
                             'passphrase': 'test123'
                         }),
                         content_type='application/json')
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert 'privateKey' in data['data']
    assert 'publicKey' in data['data']

def test_pgp_key_generation(client):
    response = client.post('/generate/pgp',
                         data=json.dumps({
                             'name': 'Test User',
                             'email': 'test@example.com',
                             'passphrase': 'test123',
                             'keyType': 'RSA',
                             'keyLength': 2048
                         }),
                         content_type='application/json')
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert 'privateKey' in data['data']
    assert 'publicKey' in data['data']

def test_invalid_passphrase_params(client):
    response = client.post('/generate/passphrase',
                         data=json.dumps({'length': 'invalid'}),
                         content_type='application/json')
    assert response.status_code == 400

def test_invalid_ssh_params(client):
    response = client.post('/generate/ssh',
                         data=json.dumps({'keyType': 'invalid'}),
                         content_type='application/json')
    assert response.status_code == 400

def test_invalid_rsa_params(client):
    response = client.post('/generate/rsa',
                         data=json.dumps({'keySize': 'invalid'}),
                         content_type='application/json')
    assert response.status_code == 400

def test_invalid_pgp_params(client):
    response = client.post('/generate/pgp',
                         data=json.dumps({'name': ''}),
                         content_type='application/json')
    assert response.status_code == 400
