import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test Passphrase Generation
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

# Test SSH Key Generation
def test_ssh_key_generation(client):
    # Test RSA key
    response = client.post('/generate/ssh',
                         data=json.dumps({
                             'keyType': 'rsa',
                             'keySize': 2048,
                             'passphrase': 'test123'
                         }),
                         content_type='application/json')
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert 'privateKey' in data['data']
    assert 'publicKey' in data['data']

    # Test ECDSA key
    response = client.post('/generate/ssh',
                         data=json.dumps({
                             'keyType': 'ecdsa',
                             'passphrase': 'test123'
                         }),
                         content_type='application/json')
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert 'privateKey' in data['data']
    assert 'publicKey' in data['data']

    # Test ED25519 key
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

# Test RSA Key Generation
def test_rsa_key_generation(client):
    for key_size in [2048, 3072, 4096]:
        response = client.post('/generate/rsa',
                             data=json.dumps({
                                 'keySize': key_size,
                                 'passphrase': 'test123'
                             }),
                             content_type='application/json')
        assert response.status_code == 200
        data = response.json
        assert data['success'] is True
        assert 'privateKey' in data['data']
        assert 'publicKey' in data['data']

# Test PGP Key Generation
def test_pgp_key_generation(client):
    # Test RSA key
    response = client.post('/generate/pgp',
                         data=json.dumps({
                             'name': 'Test User',
                             'email': 'test@example.com',
                             'keyType': 'RSA',
                             'keyLength': 2048,
                             'passphrase': 'test123'
                         }),
                         content_type='application/json')
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert 'privateKey' in data['data']
    assert 'publicKey' in data['data']

    # Test ECC key
    response = client.post('/generate/pgp',
                         data=json.dumps({
                             'name': 'Test User',
                             'email': 'test@example.com',
                             'keyType': 'ECC',
                             'curve': 'secp256k1',
                             'passphrase': 'test123'
                         }),
                         content_type='application/json')
    assert response.status_code == 200
    data = response.json
    assert data['success'] is True
    assert 'privateKey' in data['data']
    assert 'publicKey' in data['data']

# Test Invalid Parameters
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
                         data=json.dumps({'keySize': 1024}),
                         content_type='application/json')
    assert response.status_code == 400

def test_invalid_pgp_params(client):
    response = client.post('/generate/pgp',
                         data=json.dumps({'keyType': 'invalid'}),
                         content_type='application/json')
    assert response.status_code == 400
