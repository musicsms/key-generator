/**
 * Sanitize comment by removing special characters and spaces
 * 
 * @param {string} comment - The comment to sanitize
 * @returns {string} - The sanitized comment
 */
export function sanitizeComment(comment) {
    if (!comment) return '';
    return comment
        .replace(/[^a-zA-Z0-9_-]/g, '_') // Replace special chars with underscore
        .replace(/_{2,}/g, '_')          // Replace multiple underscores with single
        .slice(0, 40);                   // Limit to 40 chars
}

/**
 * Preview sanitization for UI feedback
 * 
 * @param {string} comment - The comment to preview
 * @returns {string} - The sanitized comment
 */
export function previewCommentSanitization(comment) {
    return sanitizeComment(comment);
}
