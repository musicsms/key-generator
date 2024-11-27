from flask import Flask, request, render_template, jsonify
import os
import traceback
from generators import (
    generate_passphrase,
    generate_ssh_key,
    generate_rsa_key,
    generate_pgp_key
)
from utils.utils import create_output_directory, save_key_pair
from config import config

def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    app.config.from_object(config[config_name])
    
    # Configure logging
    config[config_name].configure_logging(app)
    
    # Ensure the keys directory exists
    if not os.path.exists(app.config['KEYS_DIR']):
        os.makedirs(app.config['KEYS_DIR'])

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/generate/passphrase', methods=['POST'])
    def passphrase():
        try:
            data = request.json or {}
            result = generate_passphrase(
                length=int(data.get('length', 16)),
                include_numbers=data.get('includeNumbers', True),
                include_special=data.get('includeSpecial', True),
                exclude_chars=data.get('excludeChars', '')
            )
            
            # Ensure a consistent JSON response
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'data': {
                        'passphrase': result.get('passphrase'),
                        'length': result.get('length'),
                        'includeNumbers': result.get('includeNumbers'),
                        'includeSpecial': result.get('includeSpecial')
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'error_message': result.get('error_message', 'Failed to generate passphrase')
                }), 400
        
        except Exception as e:
            print("Passphrase Generation Error:", str(e))
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error_message': f'Failed to generate passphrase: {str(e)}'
            }), 400

    @app.route('/generate/ssh', methods=['POST'])
    def ssh():
        try:
            data = request.json or {}
            comment = data.get('comment', '').strip()
            
            # Generate the SSH key pair
            result = generate_ssh_key(
                key_type=data.get('keyType', 'rsa'),
                key_size=int(data.get('keySize', 2048)),
                passphrase=data.get('passphrase', '')
            )
            
            if result.get('success'):
                try:
                    # Create directory and save keys
                    dir_path = create_output_directory('ssh', comment)
                    private_path, public_path = save_key_pair(
                        result['privateKey'],
                        result['publicKey'],
                        dir_path,
                        'ssh'
                    )
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'privateKey': result['privateKey'],
                            'publicKey': result['publicKey'],
                            'keyType': result['keyType'],
                            'keySize': result['keySize'],
                            'directory': dir_path,
                            'privatePath': private_path,
                            'publicPath': public_path
                        }
                    })
                except Exception as e:
                    # If saving fails, still return the keys but with a warning
                    return jsonify({
                        'success': True,
                        'warning': f'Keys generated but could not be saved: {str(e)}',
                        'data': {
                            'privateKey': result['privateKey'],
                            'publicKey': result['publicKey'],
                            'keyType': result['keyType'],
                            'keySize': result['keySize']
                        }
                    })
            else:
                return jsonify({
                    'success': False,
                    'error_message': result.get('error_message', 'Failed to generate SSH key')
                }), 400
                
        except ValueError as ve:
            return jsonify({
                'success': False,
                'error_message': str(ve)
            }), 400
        except Exception as e:
            print("SSH Key Generation Error:", str(e))
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error_message': 'Internal server error'
            }), 500

    @app.route('/generate/rsa', methods=['POST'])
    def rsa():
        try:
            data = request.json or {}
            comment = data.get('comment', '').strip()
            
            # Generate the RSA key pair
            result = generate_rsa_key(
                key_size=int(data.get('keySize', 2048)),
                passphrase=data.get('passphrase', '')
            )
            
            if result.get('success'):
                try:
                    # Create directory and save keys
                    dir_path = create_output_directory('rsa', comment)
                    private_path, public_path = save_key_pair(
                        result['data']['privateKey'],
                        result['data']['publicKey'],
                        dir_path,
                        'rsa'
                    )
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'privateKey': result['data']['privateKey'],
                            'publicKey': result['data']['publicKey'],
                            'keySize': data.get('keySize', 2048),
                            'directory': dir_path,
                            'privatePath': private_path,
                            'publicPath': public_path
                        }
                    })
                except Exception as e:
                    # If saving fails, still return the keys but with a warning
                    return jsonify({
                        'success': True,
                        'warning': f'Keys generated but could not be saved: {str(e)}',
                        'data': {
                            'privateKey': result['data']['privateKey'],
                            'publicKey': result['data']['publicKey'],
                            'keySize': data.get('keySize', 2048)
                        }
                    })
            else:
                return jsonify({
                    'success': False,
                    'error_message': result.get('error_message', 'Failed to generate RSA key')
                }), 400
                
        except ValueError as ve:
            return jsonify({
                'success': False,
                'error_message': str(ve)
            }), 400
        except Exception as e:
            print("RSA Key Generation Error:", str(e))
            print(traceback.format_exc())
            return jsonify({
                'success': False,
                'error_message': 'Internal server error'
            }), 500

    @app.route('/generate/pgp', methods=['POST'])
    def pgp():
        try:
            data = request.json or {}
            
            # Required parameters
            name = data.get('name')
            email = data.get('email')
            
            if not name or not email:
                return jsonify({
                    'success': False,
                    'error_message': 'Name and email are required'
                }), 400

            # Optional parameters
            comment = data.get('comment')
            key_type = data.get('keyType', 'RSA')
            key_length = data.get('keyLength')  # Optional for RSA
            curve = data.get('curve')  # Optional for ECC
            passphrase = data.get('passphrase')
            expire_time = data.get('expireTime', '2y')

            # Validate input parameters
            if key_type not in ['RSA', 'ECC']:
                return jsonify({
                    'success': False,
                    'error_message': 'Invalid key type'
                }), 400

            if key_length and not isinstance(key_length, int):
                return jsonify({
                    'success': False,
                    'error_message': 'Invalid key length'
                }), 400

            result = generate_pgp_key(
                name=name,
                email=email,
                comment=comment,
                key_type=key_type,
                key_length=key_length,
                curve=curve,
                passphrase=passphrase,
                expire_time=expire_time
            )

            if result.get('success'):
                # Sanitize the response to remove potentially sensitive information
                sanitized_result = {
                    'success': True,
                    'data': {
                        'keyType': result.get('keyType', key_type),
                        'keyLength': result.get('keyLength', key_length),
                        'created': result.get('created')
                    }
                }
                return jsonify(sanitized_result)
            else:
                # Generic error message to prevent information leakage
                return jsonify({
                    'success': False,
                    'error_message': 'PGP key generation failed'
                }), 400

        except ValueError as ve:
            # Handle specific value errors
            return jsonify({
                'success': False,
                'error_message': 'Invalid input parameters'
            }), 400
        except Exception as e:
            # Log the full error for server-side debugging
            app.logger.error(f"PGP Key Generation Error: {str(e)}")
            app.logger.error(traceback.format_exc())
            
            # Return a generic error message
            return jsonify({
                'success': False,
                'error_message': 'Internal server error'
            }), 500

    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
