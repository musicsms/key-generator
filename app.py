from flask import Flask, request, render_template, jsonify
import os
import traceback
from generators import (
    generate_passphrase,
    generate_ssh_key,
    generate_rsa_key,
    generate_pgp_key
)

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
        print("Received SSH key generation request:", data)  # Debug logging
        
        # Ensure default values
        key_type = data.get('keyType', 'rsa')
        key_size = int(data.get('keySize', 2048))
        passphrase = data.get('passphrase')
        
        # Generate SSH key
        result = generate_ssh_key(
            key_type=key_type,
            key_size=key_size,
            passphrase=passphrase
        )
        
        # Convert to JSON response
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        print("Error in SSH key generation:", str(e))
        print(traceback.format_exc())  # Print full traceback
        return jsonify({
            'success': False,
            'error_message': f'Failed to generate SSH key: {str(e)}'
        }), 400

@app.route('/generate/rsa', methods=['POST'])
def rsa():
    try:
        data = request.json
        print("RSA Generation Request Data:", data)
        
        if not data:
            return jsonify({
                'success': False,
                'error_message': "No JSON data received"
            }), 400
            
        # Extract and validate key_size
        try:
            key_size = int(data.get('keySize', 2048))
        except (TypeError, ValueError) as e:
            return jsonify({
                'success': False,
                'error_message': f"Invalid key size format: {str(e)}"
            }), 400
            
        if key_size not in [1024, 2048, 4096]:
            return jsonify({
                'success': False,
                'error_message': 'Invalid key size. Must be 1024, 2048, or 4096'
            }), 400
            
        # Extract passphrase (can be None or empty string)
        passphrase = data.get('passphrase', '')
        
        # Generate RSA key
        result = generate_rsa_key(
            key_size=key_size,
            passphrase=passphrase
        )
        
        # Return the result directly since it's already in the correct format
        if not result.get('success', False):
            return jsonify(result), 400
            
        # Ensure we're sending the data in the correct structure
        return jsonify({
            'success': True,
            'data': result['data']
        })
    
    except Exception as e:
        print("Error in RSA key generation:", str(e))
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error_message': f'Failed to generate RSA key: {str(e)}'
        }), 400

@app.route('/generate/pgp', methods=['POST'])
def pgp():
    # Placeholder for future PGP key generation
    return jsonify({
        'success': False,
        'error_message': 'PGP key generation is not yet implemented'
    }), 501

if __name__ == '__main__':
    app.run(debug=True)
