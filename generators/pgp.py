from utils.response import info_response, error_response

def generate_pgp_key():
    """Placeholder for PGP key generation"""
    try:
        return info_response('PGP key generation is coming soon!')
    except Exception as e:
        return error_response(str(e))
