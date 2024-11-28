import pytest
import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_generate_passphrase():
    """Test passphrase generation"""
    payload = {
        "length": 16,
        "words": 4
    }
    response = requests.post(f"{BASE_URL}/generate/passphrase", json=payload, timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "passphrase" in data["data"]
    assert isinstance(data["data"]["passphrase"], str)
    assert len(data["data"]["passphrase"]) > 0

def test_generate_ssh_key():
    """Test SSH key generation"""
    payload = {
        "type": "rsa",
        "bits": 2048,
        "comment": "test_key",
        "passphrase": "test123"
    }
    response = requests.post(f"{BASE_URL}/generate/ssh", json=payload, timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "privateKey" in data["data"]
    assert "publicKey" in data["data"]
    assert data["data"]["privateKey"].startswith("-----BEGIN OPENSSH PRIVATE KEY-----")
    assert "ssh-rsa" in data["data"]["publicKey"]

def test_generate_rsa_key():
    """Test RSA key generation"""
    payload = {
        "bits": 2048,
        "comment": "test_key",
        "passphrase": "test123"
    }
    response = requests.post(f"{BASE_URL}/generate/rsa", json=payload, timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "privateKey" in data["data"]
    assert "publicKey" in data["data"]
    assert data["data"]["privateKey"].startswith("-----BEGIN")
    assert data["data"]["publicKey"].startswith("-----BEGIN PUBLIC KEY-----")

def test_generate_pgp_key():
    """Test PGP key generation"""
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "comment": "test_key",
        "key_type": "RSA",
        "key_length": 2048,
        "passphrase": "test123",
        "expire_time": "1y"
    }
    response = requests.post(f"{BASE_URL}/generate/pgp", json=payload, timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "privateKey" in data["data"]
    assert "publicKey" in data["data"]
    assert "keyId" in data["data"]
    assert data["data"]["privateKey"].startswith("-----BEGIN PGP PRIVATE KEY BLOCK-----")
    assert data["data"]["publicKey"].startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----")

def test_invalid_input():
    """Test error handling for invalid input"""
    payload = {
        "type": "invalid",
        "bits": 1024
    }
    response = requests.post(f"{BASE_URL}/generate/ssh", json=payload, timeout=5)
    assert response.status_code in [400, 422]
    data = response.json()
    assert data["success"] is False
    assert "error" in data
