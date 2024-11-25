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

# Ensure the keys directory exists
if not os.path.exists('keys'):
    os.makedirs('keys')

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
                save_key_pair(
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
                        'directory': dir_path
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
                save_key_pair(
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
                        'directory': dir_path
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
        comment = data.get('comment', '').strip()
        
        # Generate the PGP key pair
        result = generate_pgp_key(
            name=data.get('name', ''),
            email=data.get('email', ''),
            passphrase=data.get('passphrase', '')
        )
        
        if result.get('success'):
            try:
                # Create directory and save keys
                dir_path = create_output_directory('pgp', comment)
                save_key_pair(
                    result['private_key'],
                    result['public_key'],
                    dir_path,
                    'pgp'
                )
                
                return jsonify({
                    'success': True,
                    'data': {
                        'privateKey': result['private_key'],
                        'publicKey': result['public_key'],
                        'directory': dir_path
                    }
                })
            except Exception as e:
                # If saving fails, still return the keys but with a warning
                return jsonify({
                    'success': True,
                    'warning': f'Keys generated but could not be saved: {str(e)}',
                    'data': {
                        'privateKey': result['private_key'],
                        'publicKey': result['public_key']
                    }
                })
        else:
            return jsonify({
                'success': False,
                'error_message': result.get('error_message', 'Failed to generate PGP key')
            }), 400
            
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error_message': str(ve)
        }), 400
    except Exception as e:
        print("PGP Key Generation Error:", str(e))
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error_message': 'Internal server error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
