"""Flask application for key generation."""

import os
import logging
from flask import Flask, request, render_template, jsonify
from generators import (
    generate_passphrase,
    generate_ssh_key,
    generate_rsa_key,
    generate_pgp_key
)
from utils.utils import create_output_directory, save_key_pair, generate_and_save_key_pair

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Custom error messages
ERROR_MESSAGES = {
    'invalid_request': 'Invalid request parameters',
    'key_generation': 'Error generating cryptographic key',
    'key_save': 'Error saving generated key',
    'internal_error': 'An internal error occurred',
    'invalid_key_type': 'Invalid key type specified',
    'invalid_key_size': 'Invalid key size specified',
    'invalid_comment': 'Invalid comment format'
}


def error_response(error_type, status_code=400, details=None):
    """
    Generate a standardized error response.
    Never expose internal error details to the client.
    """
    error_message = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES['internal_error'])
    
    if details and app.debug:
        logger.error("%s: %s", error_message, details)
    else:
        logger.error(error_message)
    
    return jsonify({
        'success': False,
        'error': {
            'type': error_type,
            'message': error_message
        }
    }), status_code


def success_response(data, warning=None):
    """Generate a standardized success response."""
    response = {
        'success': True,
        'data': data
    }
    if warning:
        response['warning'] = warning
    return jsonify(response)

# Ensure the keys directory structure exists
try:
    base_path = os.getenv('KEY_STORAGE_PATH', 'keys')
    for key_type in ['ssh', 'rsa', 'pgp']:
        dir_path = os.path.join(base_path, key_type)
        os.makedirs(dir_path, exist_ok=True)
        os.chmod(dir_path, 0o700)
except OSError as e:
    logger.error("Failed to initialize directory structure: %s", str(e))


@app.route('/')
def index():
    """Render the main index page."""
    return render_template('index.html')


@app.route('/generate/passphrase', methods=['POST'])
def passphrase():
    """Generate a secure passphrase based on user parameters."""
    try:
        data = request.get_json(silent=True) or {}
        
        # Validate input parameters
        try:
            length = int(data.get('length', 16))
            if length < 8 or length > 64:
                return error_response('invalid_request', details='Length must be between 8 and 64')
        except ValueError:
            return error_response('invalid_request', details='Invalid length parameter')
        
        result = generate_passphrase(
            length=length,
            include_numbers=data.get('includeNumbers', True),
            include_special=data.get('includeSpecial', True),
            exclude_chars=data.get('excludeChars', '')
        )
        
        if not result.get('success'):
            return error_response('key_generation', details=result.get('error_message'))
        
        return success_response(result['data'])
    except KeyError as e:
        return error_response('invalid_request', details=f'Missing parameter: {str(e)}')
    except Exception as e:
        logger.error("Unexpected error in passphrase generation: %s", str(e))
        return error_response('internal_error', 500)


@app.route('/generate/ssh', methods=['POST'])
def ssh():
    """Generate an SSH key pair based on user parameters."""
    try:
        data = request.get_json(silent=True) or {}
        comment = data.get('comment', '').strip()
        
        try:
            key_type = data.get('keyType', 'rsa').lower()
            if key_type not in ['rsa', 'ecdsa', 'ed25519']:
                return error_response('invalid_key_type')
            
            key_size = int(data.get('keySize', 4096))
            if key_type == 'rsa' and key_size not in [2048, 3072, 4096]:
                return error_response('invalid_key_size', details='RSA key size must be 2048, 3072, or 4096 bits')
        except ValueError:
            return error_response('invalid_key_size')
        
        # Use the new utility function for key generation and saving
        result = generate_and_save_key_pair('ssh', key_type, comment, generate_ssh_key, key_size=key_size, passphrase=data.get('passphrase', ''))
        
        return success_response(result)
    except KeyError as e:
        return error_response('invalid_request', details=f'Missing parameter: {str(e)}')
    except Exception as e:
        logger.error("SSH key generation failed: %s", str(e))
        return error_response('internal_error', 500)


@app.route('/generate/rsa', methods=['POST'])
def rsa():
    """Generate an RSA key pair based on user parameters."""
    try:
        data = request.get_json(silent=True) or {}
        comment = data.get('comment', '').strip()
        
        try:
            key_size = int(data.get('keySize', 4096))
            if key_size not in [2048, 3072, 4096]:
                return error_response('invalid_key_size', details='RSA key size must be 2048, 3072, or 4096 bits')
        except ValueError:
            return error_response('invalid_key_size')
        
        # Use the new utility function for key generation and saving
        result = generate_and_save_key_pair('rsa', key_size, comment, generate_rsa_key, passphrase=data.get('passphrase', ''))
        
        return success_response(result)
    except KeyError as e:
        return error_response('invalid_request', details=f'Missing parameter: {str(e)}')
    except Exception as e:
        logger.error("RSA key generation failed: %s", str(e))
        return error_response('internal_error', 500)


@app.route('/generate/pgp', methods=['POST'])
def pgp():
    """Generate a PGP key pair based on user parameters."""
    try:
        data = request.get_json(silent=True) or {}
        
        try:
            name = data['name'].strip()
            email = data['email'].strip()
            comment = data.get('comment', '').strip()
            key_type = data.get('keyType', 'RSA').upper()
            key_length = int(data.get('keyLength', 2048))
            curve = data.get('curve', 'secp256k1')
            expire_time = data.get('expireTime', '2y')
            
            if key_type == 'RSA' and key_length not in [2048, 3072, 4096]:
                return error_response('invalid_key_size', details='RSA key size must be 2048, 3072, or 4096 bits')
            
            if key_type == 'ECC' and curve not in ['secp256k1', 'secp384r1', 'secp521r1', 'brainpoolP256r1', 'brainpoolP384r1', 'brainpoolP512r1']:
                return error_response('invalid_key_type', details='Invalid ECC curve specified')
        except (ValueError, KeyError):
            return error_response('invalid_request')
        
        # Use the new utility function for key generation and saving
        result = generate_and_save_key_pair('pgp', key_type, comment, generate_pgp_key, name=name, email=email, key_length=key_length, curve=curve, passphrase=data.get('passphrase', ''), expire_time=expire_time)
        
        return success_response(result)
    except KeyError as e:
        return error_response('invalid_request', details=f'Missing parameter: {str(e)}')
    except Exception as e:
        logger.error("PGP key generation failed: %s", str(e))
        return error_response('internal_error', 500)


@app.route('/health')
def health_check():
    """Perform a health check of the application."""
    return jsonify({'status': 'healthy'})


# Security headers
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response


# Handle all unhandled exceptions without exposing internal details
@app.errorhandler(Exception)
def handle_error(error):
    """Handle unexpected errors gracefully."""
    logger.error("Unhandled exception: %s", str(error))
    return error_response('internal_error', 500)


if __name__ == '__main__':
    # Ensure we're not in debug mode in production
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    host = os.environ.get('HOST', '127.0.0.1')  # Default to localhost
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=debug_mode)
