/**
 * Sanitize and validate comment for key generation.
 * Follows the same rules as the backend:
 * - Allows alphanumeric, hyphen, underscore, and period
 * - Replaces spaces with underscores
 * - Maximum length of 64 characters
 * 
 * @param {string} comment - The comment to validate
 * @returns {string} - The sanitized comment
 * @throws {Error} - If comment is invalid after sanitization
 */
export function validateComment(comment) {
    if (!comment) {
        return '';
    }

    // Replace spaces with underscores
    let sanitized = comment.replace(/\s+/g, '_');
    
    // Remove any characters that aren't alphanumeric, hyphen, underscore, or period
    sanitized = sanitized.replace(/[^\w\-\.]/g, '');
    
    // Limit length to 64 characters
    sanitized = sanitized.slice(0, 64);

    // If original comment wasn't empty but sanitized is, the comment was invalid
    if (!sanitized && comment) {
        throw new Error(
            'Invalid comment. Comment can only contain letters, numbers, ' +
            'spaces, hyphens, underscores, and periods. Spaces will be ' +
            'replaced with underscores.'
        );
    }

    return sanitized;
}

/**
 * Preview comment sanitization without throwing errors.
 * Useful for showing users how their comment will be processed.
 * 
 * @param {string} comment - The comment to preview
 * @returns {string} - The sanitized comment or empty string if invalid
 */
export function previewCommentSanitization(comment) {
    try {
        return validateComment(comment);
    } catch (e) {
        return '';
    }
}
