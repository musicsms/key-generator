// Utility functions for the key generator application

export function clearOutputs() {
    // Reset all output elements
    const elementsToReset = [
        { id: 'resultSection', action: 'display', value: 'none' },
        { id: 'customResult', action: 'innerHTML', value: '' },
        { id: 'passphraseResult', action: 'display', value: 'none' },
        { id: 'keyPairResult', action: 'display', value: 'none' },
        { id: 'publicKey', action: 'value', value: '' },
        { id: 'privateKey', action: 'value', value: '' },
        { id: 'passphrase', action: 'value', value: '' }
    ];

    elementsToReset.forEach(item => {
        const element = document.getElementById(item.id);
        if (element) {
            if (item.action === 'display') {
                element.style.display = item.value;
            } else if (item.action === 'innerHTML') {
                element.innerHTML = item.value;
            } else if (item.action === 'value') {
                element.value = item.value;
            }
        }
    });

    // Hide any visible result sections
    const resultSections = document.querySelectorAll('.result-section');
    resultSections.forEach(section => {
        section.style.display = 'none';
    });
}

export function displayMessage(message, type = 'info') {
    clearOutputs();
    const resultSection = document.getElementById('resultSection');
    const customResult = document.getElementById('customResult');
    
    if (resultSection && customResult) {
        resultSection.style.display = 'block';
        customResult.innerHTML = `
            <div class="alert alert-${type}" role="alert">
                ${message}
            </div>
        `;
    }
}

export function showLoading() {
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.disabled = true;
        const originalText = button.innerHTML;
        button.setAttribute('data-original-text', originalText);
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...';
    });
}

export function hideLoading() {
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text') || 'Generate';
    });
}

export function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const textToCopy = element.value || element.textContent;
    
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(textToCopy).then(() => {
            displayMessage('Copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        try {
            document.execCommand('copy');
            displayMessage('Copied to clipboard!', 'success');
        } finally {
            textArea.remove();
        }
    }
}

export function togglePasswordHandler(event) {
    const button = event.currentTarget;
    const inputGroup = button.closest('.input-group');
    if (!inputGroup) {
        console.error('No input group found for toggle password button');
        return;
    }

    const passwordInput = inputGroup.querySelector('input[type="password"], input[type="text"]');
    if (!passwordInput) {
        console.error('No password input found in input group');
        return;
    }

    const icon = button.querySelector('i');
    if (!icon) {
        console.error('No icon found in toggle button');
        return;
    }

    console.log('Toggling password visibility');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
    }
}

export function attachTogglePassword() {
    console.log('Attaching toggle password handlers');
    document.querySelectorAll('.toggle-password').forEach(button => {
        // Remove any existing listeners to prevent duplicates
        button.removeEventListener('click', togglePasswordHandler);
        button.addEventListener('click', togglePasswordHandler);
        console.log('Attached toggle handler to button:', button);
    });
}
