from flask import jsonify

def success_response(data):
    """Create a success response with data"""
    return {
        'success': True,
        'data': data
    }

def error_response(message, status_code=500):
    """Create an error response with message"""
    return {
        'success': False,
        'error_message': str(message)
    }

def info_response(message):
    """Create an info response with message"""
    return {
        'success': True,
        'data': {
            'message': message
        }
    }
