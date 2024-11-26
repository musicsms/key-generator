import re

def sanitize_comment(comment):
    """
    Sanitize comment for safe folder creation.
    Allows alphanumeric, hyphen, underscore, and period.
    Replaces spaces with underscores.
    
    Args:
        comment (str): Original comment
        
    Returns:
        str: Sanitized comment safe for folder names
    """
    if not comment:
        return ""
    
    # Replace spaces with underscores
    comment = comment.replace(" ", "_")
    
    # Remove any characters that aren't alphanumeric, hyphen, underscore, or period
    comment = re.sub(r'[^\w\-\.]', '', comment)
    
    # Limit length to 64 characters
    return comment[:64]

def validate_comment(comment):
    """
    Validate a comment and return sanitized version or raise ValueError.
    
    Args:
        comment (str): Comment to validate
        
    Returns:
        str: Sanitized comment
        
    Raises:
        ValueError: If comment is invalid after sanitization
    """
    sanitized = sanitize_comment(comment)
    if not sanitized and comment:
        raise ValueError(
            "Invalid comment. Comment can only contain letters, numbers, "
            "spaces, hyphens, underscores, and periods. Spaces will be "
            "replaced with underscores."
        )
    return sanitized
