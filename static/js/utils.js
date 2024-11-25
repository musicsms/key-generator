// Utility functions for the key generator application

export function clearOutputs() {
    // More comprehensive clearing of all possible result elements
    const elementsToReset = [
        { id: 'resultSection', action: 'display', value: 'none' },
        { id: 'customResult', action: 'innerHTML', value: '' },
        { id: 'passphraseResult', action: 'display', value: 'none' },
        { id: 'keyPairResult', action: 'display', value: 'none' },
        { id: 'publicKey', action: 'value', value: '' },
        { id: 'privateKey', action: 'value', value: '' },
        { id: 'passphrase', action: 'value', value: '' }
    ];

    // Detailed logging of reset process
    console.log('Clearing outputs - Starting reset');

    elementsToReset.forEach(item => {
        const element = document.getElementById(item.id);
        if (element) {
            if (item.action === 'display') {
                element.style.display = item.value;
                console.log(`Reset display for ${item.id} to ${item.value}`);
            } else if (item.action === 'innerHTML') {
                element.innerHTML = item.value;
                console.log(`Reset innerHTML for ${item.id}`);
            } else if (item.action === 'value') {
                element.value = item.value;
                console.log(`Reset value for ${item.id}`);
            }
        } else {
            console.log(`Element ${item.id} not found`);
        }
    });

    // Explicitly hide any visible result sections
    const resultSections = document.querySelectorAll('.result-section');
    resultSections.forEach(section => {
        section.style.display = 'none';
        console.log('Hiding result section:', section.id);
    });

    console.log('Clearing outputs - Reset complete');
}

export function displayMessage(message, type = 'info') {
    // Log the message display attempt
    console.log('Displaying message:', { 
        message: message, 
        type: type 
    });

    clearOutputs();
    const resultSection = document.getElementById('resultSection');
    const customResult = document.getElementById('customResult');
    
    // Log element existence
    console.log('Display Message Elements:', {
        resultSection: !!resultSection,
        customResult: !!customResult
    });
    
    if (resultSection && customResult) {
        // Show result section
        resultSection.style.display = 'block';
        console.log('Result section display set to block');

        // Set custom result HTML
        customResult.innerHTML = `
            <div class="alert alert-${type}" role="alert">
                ${message}
            </div>
        `;
        console.log('Custom result HTML set');
    } else {
        console.error('Failed to display message: missing elements');
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
    if (!element) {
        console.error(`Element with id ${elementId} not found`);
        return;
    }

    // Create a temporary textarea to copy from
    const tempTextArea = document.createElement('textarea');
    tempTextArea.value = element.value || element.textContent;
    
    // Make the textarea out of viewport
    tempTextArea.style.position = 'fixed';
    tempTextArea.style.left = '-9999px';
    document.body.appendChild(tempTextArea);
    
    // Select the text
    tempTextArea.select();
    tempTextArea.setSelectionRange(0, 99999); // For mobile devices
    
    try {
        // Copy the text
        const successful = document.execCommand('copy');
        const msg = successful ? 'Copied!' : 'Copy failed';
        
        // Optional: Show a temporary tooltip or message
        const originalBtnText = element.textContent;
        const copyButton = document.querySelector(`button[onclick="copyToClipboard('${elementId}')"]`);
        
        if (copyButton) {
            const originalHTML = copyButton.innerHTML;
            copyButton.innerHTML = '<i class="bi bi-check-lg text-success"></i>';
            
            setTimeout(() => {
                copyButton.innerHTML = originalHTML;
            }, 2000);
        }
    } catch (err) {
        console.error('Unable to copy', err);
    }
    
    // Remove the temporary textarea
    document.body.removeChild(tempTextArea);
}

export function togglePasswordHandler(event) {
    const button = event.currentTarget;
    const inputGroup = button.closest('.input-group');
    const passwordInput = inputGroup.querySelector('input[type="password"], input[type="text"]');
    const icon = button.querySelector('i');
    
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
    // No longer needed as we're using inline handlers
    console.log('Password toggle handlers are now inline');
}
