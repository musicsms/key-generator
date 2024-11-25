import secrets
import string
import sys
import traceback

def generate_passphrase(length=16, include_numbers=True, include_special=True, exclude_chars=''):
    """Generate a secure passphrase with specified options"""
    try:
        # Validate length
        if length < 8 or length > 64:
            return {
                'success': False,
                'error_message': 'Passphrase length must be between 8 and 64 characters'
            }
        
        # Define character sets
        chars = string.ascii_letters
        
        if include_numbers:
            chars += string.digits
        
        if include_special:
            chars += string.punctuation
        
        # Remove excluded characters
        if exclude_chars:
            chars = ''.join(c for c in chars if c not in exclude_chars)
        
        # Validate character pool
        if not chars:
            return {
                'success': False,
                'error_message': 'No valid characters available after exclusions'
            }
        
        # Generate passphrase
        passphrase = ''.join(secrets.choice(chars) for _ in range(length))
        
        return {
            'success': True,
            'passphrase': passphrase,
            'length': length,
            'includeNumbers': include_numbers,
            'includeSpecial': include_special
        }
    
    except Exception as e:
        # Comprehensive error logging
        error_details = {
            'success': False,
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc(),
            'python_version': sys.version,
            'platform': sys.platform
        }
        
        # Log error details
        print("Passphrase Generation Error Details:")
        for key, value in error_details.items():
            print(f"{key}: {value}")
        
        return error_details
