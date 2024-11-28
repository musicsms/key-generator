// Utility functions for the key generator application

export function clearOutputs() {
    // Clear all result sections
    document.querySelectorAll('.result-section').forEach(section => {
        section.innerHTML = '';
    });
}

export function displayMessage(message, type = 'info') {
    const activeTab = document.querySelector('.tab-pane.active');
    if (!activeTab) return;

    const resultSection = activeTab.querySelector('.result-section');
    if (resultSection) {
        resultSection.innerHTML = `
            <div class="alert alert-${type}" role="alert">
                ${message}
            </div>
        `;
    }
}

export function showLoading() {
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...';
    });
}

export function hideLoading() {
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.disabled = false;
        button.innerHTML = button.innerHTML.replace('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...', 'Generate');
    });
}

export async function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    try {
        const text = element.innerText || element.value;
        await navigator.clipboard.writeText(text);
        
        // Show success message
        const copyBtn = document.querySelector(`[data-target="${elementId}"]`);
        if (copyBtn) {
            const originalText = copyBtn.innerText;
            copyBtn.innerText = 'Copied!';
            setTimeout(() => {
                copyBtn.innerText = originalText;
            }, 2000);
        }

        // Show a temporary success message
        const messageDiv = document.createElement('div');
        messageDiv.className = 'alert alert-success position-fixed bottom-0 end-0 m-3';
        messageDiv.style.zIndex = '1050';
        messageDiv.textContent = 'Copied to clipboard!';
        document.body.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.remove();
        }, 2000);
    } catch (err) {
        console.error('Failed to copy text: ', err);
        displayMessage('Failed to copy to clipboard', 'danger');
    }
}

export function togglePasswordHandler(event) {
    const button = event.currentTarget;
    const inputId = button.getAttribute('data-toggle-password');
    const input = document.getElementById(inputId);
    
    if (!input) return;
    
    const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
    input.setAttribute('type', type);
    
    // Update icon
    const icon = button.querySelector('i');
    if (icon) {
        if (type === 'password') {
            icon.classList.remove('bi-eye-slash');
            icon.classList.add('bi-eye');
        } else {
            icon.classList.remove('bi-eye');
            icon.classList.add('bi-eye-slash');
        }
    }
}

export function attachTogglePassword() {
    document.querySelectorAll('[data-toggle-password]').forEach(button => {
        button.addEventListener('click', togglePasswordHandler);
    });
}
