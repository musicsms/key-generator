import pytest
import os
import sys
from pathlib import Path
import tempfile
import shutil
import stat

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from generators import (
    generate_passphrase,
    generate_ssh_key,
    generate_rsa_key,
    generate_pgp_key
)

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

def test_passphrase_generation():
    """Test passphrase generation with default parameters"""
    result = generate_passphrase()
    assert result['success'] is True
    assert isinstance(result['passphrase'], str)
    assert len(result['passphrase']) == 16

def test_passphrase_generation_custom_length():
    """Test passphrase generation with custom length"""
    result = generate_passphrase(length=32)
    assert result['success'] is True
    assert isinstance(result['passphrase'], str)
    assert len(result['passphrase']) == 32

def test_ssh_key_generation():
    """Test SSH key generation with RSA"""
    result = generate_ssh_key(key_type='rsa', comment='test')
    assert result['success'] is True
    assert result['data']['privateKey'].startswith('-----BEGIN')
    assert result['data']['publicKey'].startswith('ssh-rsa')

def test_ssh_key_generation_ed25519():
    """Test SSH key generation with ED25519"""
    result = generate_ssh_key(key_type='ed25519', comment='test')
    assert result['success'] is True
    assert result['data']['privateKey'].startswith('-----BEGIN')
    assert result['data']['publicKey'].startswith('ssh-ed25519')

def test_rsa_key_generation():
    """Test RSA key generation"""
    result = generate_rsa_key(key_size=2048)
    assert result['success'] is True
    assert result['data']['privateKey'].startswith('-----BEGIN')
    assert result['data']['publicKey'].startswith('-----BEGIN PUBLIC KEY-----')

def test_pgp_key_generation_rsa(gpg_home):
    """Test PGP key generation with RSA"""
    result = generate_pgp_key(
        name='Test User',
        email='test@example.com',
        key_type='RSA',
        key_length=2048,
        passphrase='test123',
        expire_time='2y',
        comment='Test Key'
    )
    assert result['success'] is True
    assert result['data']['privateKey'].startswith('-----BEGIN PGP PRIVATE KEY BLOCK-----')
    assert result['data']['publicKey'].startswith('-----BEGIN PGP PUBLIC KEY BLOCK-----')
    assert result['data']['keyType'] == 'RSA'
    assert result['data']['keyLength'] == 2048
    assert result['data']['name'] == 'Test User'
    assert result['data']['email'] == 'test@example.com'
    assert result['data']['comment'] == 'Test Key'
    assert result['data']['expireDate'] is not None

def test_pgp_key_generation_ecc(gpg_home):
    """Test PGP key generation with ECC"""
    result = generate_pgp_key(
        name='ECC User',
        email='ecc@example.com',
        key_type='ECC',
        curve='secp384r1',
        expire_time='1y'
    )
    assert result['success'] is True
    assert result['data']['privateKey'].startswith('-----BEGIN PGP PRIVATE KEY BLOCK-----')
    assert result['data']['publicKey'].startswith('-----BEGIN PGP PUBLIC KEY BLOCK-----')
    assert result['data']['keyType'] == 'ECC'
    assert result['data']['curve'] == 'secp384r1'
    assert result['data']['name'] == 'ECC User'
    assert result['data']['email'] == 'ecc@example.com'

def test_invalid_pgp_params(gpg_home):
    """Test comprehensive error handling for PGP key generation"""
    # Test invalid name
    result = generate_pgp_key(name='', email='test@example.com')
    assert result['success'] is False
    assert 'Name must be a non-empty string' in result['error_message']

    # Test invalid email
    result = generate_pgp_key(name='Test User', email='invalid-email')
    assert result['success'] is False
    assert 'Invalid email format' in result['error_message']

    # Test invalid key type
    result = generate_pgp_key(name='Test User', email='test@example.com', key_type='INVALID')
    assert result['success'] is False
    assert 'Invalid key type' in result['error_message']

    # Test invalid RSA key length
    result = generate_pgp_key(
        name='Test User', 
        email='test@example.com', 
        key_type='RSA', 
        key_length=1024
    )
    assert result['success'] is False
    assert 'Invalid key length for RSA' in result['error_message']

    # Test invalid ECC curve
    result = generate_pgp_key(
        name='Test User', 
        email='test@example.com', 
        key_type='ECC', 
        curve='invalid-curve'
    )
    assert result['success'] is False
    assert 'Invalid curve' in result['error_message']

    # Test invalid expire time
    result = generate_pgp_key(
        name='Test User', 
        email='test@example.com', 
        expire_time='invalid'
    )
    assert result['success'] is False
    assert 'Invalid expiration time format' in result['error_message']

def test_pgp_key_generation_with_special_characters(gpg_home):
    """Test PGP key generation with special characters in name and comment"""
    result = generate_pgp_key(
        name='Test User <Special>',
        email='special@example.com',
        comment='Test & Special Key'
    )
    assert result['success'] is True
    assert result['data']['name'] == 'Test User Special'
    assert result['data']['email'] == 'special@example.com'

def test_pgp_key_generation_long_inputs(gpg_home):
    """Test PGP key generation with long inputs"""
    long_name = 'A' * 150  # Longer than max allowed length
    long_email = 'a' * 50 + '@example.com'
    
    result = generate_pgp_key(
        name=long_name, 
        email=long_email,
        comment='Long Input Test'
    )
    assert result['success'] is True
    assert len(result['data']['name']) <= 100
    assert result['data']['email'] == long_email

def test_invalid_passphrase_length():
    """Test error handling for invalid passphrase length"""
    result = generate_passphrase(length=-1)
    assert result['success'] is False
    assert 'error_message' in result

def test_invalid_ssh_type():
    """Test error handling for invalid SSH key type"""
    result = generate_ssh_key(key_type='invalid')
    assert result['success'] is False
    assert 'error_message' in result

def test_invalid_rsa_size():
    """Test error handling for invalid RSA key size"""
    result = generate_rsa_key(key_size=1024)
    assert result['success'] is False
    assert 'error_message' in result
