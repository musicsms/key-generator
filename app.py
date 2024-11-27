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

app = Flask(__name__)

# Ensure the keys directory structure exists
base_path = os.getenv('KEY_STORAGE_PATH', 'keys')
for key_type in ['ssh', 'rsa', 'pgp']:
    dir_path = os.path.join(base_path, key_type)
    os.makedirs(dir_path, exist_ok=True)
    os.chmod(dir_path, 0o700)

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
        
        # Get key_size if provided, otherwise let generator use default
        key_size = data.get('keySize')
        if key_size is not None:
            key_size = int(key_size)
        
        # Generate the SSH key pair
        result = generate_ssh_key(
            key_type=data.get('keyType', 'rsa'),
            key_size=key_size,
            comment=comment,
            passphrase=data.get('passphrase', '')
        )
        
        if not isinstance(result, dict):
            return jsonify({
                'success': False,
                'error_message': str(result)
            }), 400
            
        if result.get('success'):
            try:
                # Create directory and save keys
                dir_path = create_output_directory('ssh', comment)
                private_path, public_path = save_key_pair(
                    result['data']['privateKey'],
                    result['data']['publicKey'],
                    dir_path,
                    'ssh'
                )
                
                return jsonify({
                    'success': True,
                    'data': {
                        'privateKey': result['data']['privateKey'],
                        'publicKey': result['data']['publicKey'],
                        'keyType': result['data']['keyType'],
                        'keySize': result['data']['keySize'],
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
                        'keyType': result['data']['keyType'],
                        'keySize': result['data']['keySize']
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
            'error_message': f'Failed to generate SSH key: {str(e)}'
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
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        print("PGP Key Generation Error:", str(e))
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error_message': f'Failed to generate PGP key: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
