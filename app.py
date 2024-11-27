from flask import Flask, request, render_template, jsonify
import os
import logging
from generators import (
    generate_passphrase,
    generate_ssh_key,
    generate_rsa_key,
    generate_pgp_key
)
from utils.utils import create_output_directory, save_key_pair

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
        logger.error(f"{error_message}: {details}")
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
except Exception as e:
    logger.error(f"Failed to initialize directory structure: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate/passphrase', methods=['POST'])
def passphrase():
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
        
        return success_response({
            'passphrase': result['passphrase'],
            'length': length,
            'includeNumbers': data.get('includeNumbers', True),
            'includeSpecial': data.get('includeSpecial', True)
        })
        
    except Exception as e:
        logger.error(f"Passphrase generation failed: {str(e)}")
        return error_response('internal_error', 500)

@app.route('/generate/ssh', methods=['POST'])
def ssh():
    try:
        data = request.get_json(silent=True) or {}
        comment = data.get('comment', '').strip()
        
        # Validate key_size
        key_size = data.get('keySize')
        if key_size is not None:
            try:
                key_size = int(key_size)
            except ValueError:
                return error_response('invalid_key_size')
        
        # Generate the SSH key pair
        result = generate_ssh_key(
            key_type=data.get('keyType', 'ed25519'),
            key_size=key_size,
            comment=comment,
            passphrase=data.get('passphrase', '')
        )
        
        if not result.get('success'):
            return error_response('key_generation', details=result.get('error_message'))
        
        try:
            # Create directory and save keys
            dir_path = create_output_directory('ssh', comment)
            private_path, public_path = save_key_pair(
                result['data']['privateKey'],
                result['data']['publicKey'],
                dir_path,
                'ssh'
            )
            
            return success_response({
                'privateKey': result['data']['privateKey'],
                'publicKey': result['data']['publicKey'],
                'keyType': result['data']['keyType'],
                'keySize': result['data']['keySize'],
                'directory': dir_path,
                'privatePath': private_path,
                'publicPath': public_path
            })
            
        except Exception as e:
            logger.error(f"Failed to save SSH key: {str(e)}")
            return success_response({
                'privateKey': result['data']['privateKey'],
                'publicKey': result['data']['publicKey'],
                'keyType': result['data']['keyType'],
                'keySize': result['data']['keySize']
            }, warning='Keys generated but could not be saved')
            
    except Exception as e:
        logger.error(f"SSH key generation failed: {str(e)}")
        return error_response('internal_error', 500)

@app.route('/generate/rsa', methods=['POST'])
def rsa():
    try:
        data = request.get_json(silent=True) or {}
        comment = data.get('comment', '').strip()
        
        try:
            key_size = int(data.get('keySize', 4096))
            if key_size not in [3072, 4096]:
                return error_response('invalid_key_size', details='RSA key size must be 3072 or 4096 bits')
        except ValueError:
            return error_response('invalid_key_size')
        
        # Generate the RSA key pair
        result = generate_rsa_key(
            key_size=key_size,
            passphrase=data.get('passphrase', '')
        )
        
        if not result.get('success'):
            return error_response('key_generation', details=result.get('error_message'))
        
        try:
            # Create directory and save keys
            dir_path = create_output_directory('rsa', comment)
            private_path, public_path = save_key_pair(
                result['data']['privateKey'],
                result['data']['publicKey'],
                dir_path,
                'rsa'
            )
            
            return success_response({
                'privateKey': result['data']['privateKey'],
                'publicKey': result['data']['publicKey'],
                'keySize': key_size,
                'directory': dir_path,
                'privatePath': private_path,
                'publicPath': public_path
            })
            
        except Exception as e:
            logger.error(f"Failed to save RSA key: {str(e)}")
            return success_response({
                'privateKey': result['data']['privateKey'],
                'publicKey': result['data']['publicKey'],
                'keySize': key_size
            }, warning='Keys generated but could not be saved')
            
    except Exception as e:
        logger.error(f"RSA key generation failed: {str(e)}")
        return error_response('internal_error', 500)

@app.route('/generate/pgp', methods=['POST'])
def pgp():
    try:
        data = request.get_json(silent=True) or {}
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        comment = data.get('comment', '').strip()
        
        if not name or not email:
            return error_response('invalid_request', details='Name and email are required')
        
        result = generate_pgp_key(
            name=name,
            email=email,
            comment=comment,
            passphrase=data.get('passphrase', '')
        )
        
        if not result.get('success'):
            return error_response('key_generation', details=result.get('error_message'))
        
        try:
            # Create directory and save keys
            dir_path = create_output_directory('pgp', comment)
            private_path, public_path = save_key_pair(
                result['data']['privateKey'],
                result['data']['publicKey'],
                dir_path,
                'pgp'
            )
            
            return success_response({
                'privateKey': result['data']['privateKey'],
                'publicKey': result['data']['publicKey'],
                'keyId': result['data']['keyId'],
                'directory': dir_path,
                'privatePath': private_path,
                'publicPath': public_path
            })
            
        except Exception as e:
            logger.error(f"Failed to save PGP key: {str(e)}")
            return success_response({
                'privateKey': result['data']['privateKey'],
                'publicKey': result['data']['publicKey'],
                'keyId': result['data']['keyId']
            }, warning='Keys generated but could not be saved')
            
    except Exception as e:
        logger.error(f"PGP key generation failed: {str(e)}")
        return error_response('internal_error', 500)

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.errorhandler(Exception)
def handle_error(error):
    """Handle all unhandled exceptions without exposing internal details"""
    logger.error(f"Unhandled error: {str(error)}")
    return error_response('internal_error', 500)

if __name__ == '__main__':
    # Ensure we're not in debug mode in production
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if debug_mode else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
