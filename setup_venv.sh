#!/bin/bash

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    rm -rf venv
fi

# Create new virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install build dependencies
brew install openssl

# Set environment variables for compilation
export LDFLAGS="-L/opt/homebrew/opt/openssl/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl/include"

# Install required packages with verbose output
pip install --verbose cryptography paramiko

# Deactivate virtual environment
deactivate

echo "Virtual environment setup complete!"
