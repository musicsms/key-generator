// Generation handlers for different key types
import { showLoading, hideLoading, displayMessage, copyToClipboard, clearOutputs } from './utils.js';
import { validateComment } from './validation.js';

// Helper function to get the output section for the current tab
function getResultSection() {
    const activeTab = document.querySelector('.tab-pane.active');
    if (!activeTab) return null;
    return activeTab.querySelector('.result-section');
}

export function handlePassphraseGeneration(e) {
    e.preventDefault();
    e.stopPropagation();
    const form = e.target;
    const formData = new FormData(form);
    
    // Validate length input
    const lengthInput = form.querySelector('input[name="length"]');
    const length = parseInt(formData.get('length') || 16);
    
    // Additional client-side validation
    if (length < 8 || length > 64) {
        displayMessage('Passphrase length must be between 8 and 64 characters', 'danger');
        return;
    }
    
    // Convert form data to object and ensure boolean values
    const data = {
        length: length,
        includeNumbers: formData.get('includeNumbers') === 'on',
        includeSpecial: formData.get('includeSpecial') === 'on',
        excludeChars: formData.get('excludeChars') || ''
    };

    // Show loading state
    showLoading();

    // Send request to generate passphrase
    fetch('/generate/passphrase', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        hideLoading();
        if (!response.ok) {
            throw new Error('Failed to generate passphrase');
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            displayPassphrase(result.data.passphrase);
        } else {
            throw new Error(result.error_message || 'No passphrase generated');
        }
    })
    .catch(error => {
        hideLoading();
        displayMessage(error.message || 'An error occurred while generating the passphrase', 'danger');
    });
}

export function handleSSHKeyGeneration(e) {
    e.preventDefault();
    e.stopPropagation();
    clearOutputs();
    
    try {
        const form = e.target;
        const formData = new FormData(form);
        
        // Validate and sanitize inputs
        const comment = validateComment(formData.get('comment'));
        const keyType = formData.get('keyType');
        const keySize = parseInt(formData.get('keySize'));
        const passphrase = formData.get('passphrase');

        showLoading();

        // Make API request
        fetch('/generate/ssh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                comment: comment,
                keyType: keyType,
                keySize: keySize,
                passphrase: passphrase
            })
        })
        .then(response => response.json())
        .then(result => {
            hideLoading();
            if (result.success) {
                displayMessage(`SSH key pair generated successfully!`, 'success');
                displayKeys(result.data.privateKey, result.data.publicKey);
            } else {
                displayMessage(result.error_message || 'Failed to generate SSH key', 'danger');
            }
        })
        .catch(error => {
            hideLoading();
            displayMessage('Failed to generate SSH key: ' + error.message, 'danger');
        });
    } catch (error) {
        displayMessage(error.message, 'danger');
    }
}

export function handleRSAKeyGeneration(e) {
    e.preventDefault();
    e.stopPropagation();
    clearOutputs();
    
    try {
        const form = e.target;
        const formData = new FormData(form);
        
        // Validate and sanitize inputs
        const comment = validateComment(formData.get('comment'));
        const keySize = parseInt(formData.get('keySize'));
        const passphrase = formData.get('passphrase');

        showLoading();

        // Make API request
        fetch('/generate/rsa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                comment: comment,
                keySize: keySize,
                passphrase: passphrase
            })
        })
        .then(response => response.json())
        .then(result => {
            hideLoading();
            if (result.success) {
                displayMessage(`RSA key pair generated successfully!`, 'success');
                displayKeys(result.data.privateKey, result.data.publicKey);
            } else {
                displayMessage(result.error_message || 'Failed to generate RSA key', 'danger');
            }
        })
        .catch(error => {
            hideLoading();
            displayMessage('Failed to generate RSA key: ' + error.message, 'danger');
        });
    } catch (error) {
        displayMessage(error.message, 'danger');
    }
}

export async function handlePGPKeyGeneration(e) {
    e.preventDefault();
    e.stopPropagation();
    clearOutputs();
    
    try {
        const form = e.target;
        const formData = new FormData(form);
        
        // Validate and sanitize inputs
        const comment = validateComment(formData.get('comment'));
        const keyType = formData.get('keyType');
        const keyLength = parseInt(formData.get('keyLength'));
        const name = formData.get('name').trim();
        const email = formData.get('email').trim();
        const passphrase = formData.get('passphrase');
        const expireTime = formData.get('expireTime');

        // Additional validations
        if (!name || !email) {
            throw new Error('Name and email are required for PGP keys');
        }

        if (keyLength !== 2048 && keyLength !== 4096) {
            throw new Error('Key length must be 2048 or 4096 bits');
        }

        showLoading();

        // Make API request
        const response = await fetch('/generate/pgp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                comment: comment,
                keyType: keyType,
                keyLength: keyLength,
                passphrase: passphrase,
                expireTime: expireTime
            })
        });

        const result = await response.json();
        hideLoading();

        if (!result.success) {
            throw new Error(result.error_message || 'Failed to generate PGP key');
        }

        displayMessage(`PGP key pair generated successfully!`, 'success');
        displayKeys(result.data.privateKey, result.data.publicKey);

        // Display additional information
        const resultSection = getResultSection();
        if (resultSection) {
            const infoDiv = document.createElement('div');
            infoDiv.className = 'alert alert-info mt-3';
            infoDiv.innerHTML = `
                <h5>Key Information:</h5>
                <ul>
                    <li>Key Type: ${result.data.keyType}</li>
                    <li>Key Length: ${result.data.keyLength} bits</li>
                    <li>Key ID: ${result.data.keyId}</li>
                    <li>Expiration: ${result.data.expireDate}</li>
                    <li>Files saved in: ${result.data.directory}</li>
                </ul>
            `;
            resultSection.appendChild(infoDiv);
        }

    } catch (error) {
        hideLoading();
        displayMessage(error.message, 'danger');
    }
}

function displayKeys(privateKey, publicKey) {
    const resultSection = getResultSection();
    if (!resultSection) return;

    resultSection.innerHTML = `
        <div class="alert alert-success mb-3">
            <div class="d-flex justify-content-between align-items-center">
                <strong>Private Key:</strong>
                <button class="btn btn-sm btn-outline-success copy-btn" data-target="privateKey">Copy</button>
            </div>
            <pre id="privateKey" class="mt-2 mb-0">${privateKey}</pre>
        </div>
        <div class="alert alert-success">
            <div class="d-flex justify-content-between align-items-center">
                <strong>Public Key:</strong>
                <button class="btn btn-sm btn-outline-success copy-btn" data-target="publicKey">Copy</button>
            </div>
            <pre id="publicKey" class="mt-2 mb-0">${publicKey}</pre>
        </div>
    `;

    // Add click handlers for copy buttons
    resultSection.querySelectorAll('.copy-btn').forEach(button => {
        const textId = button.getAttribute('data-target');
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            copyToClipboard(textId);
        });
    });
}

export function displayPassphrase(passphrase) {
    const resultSection = getResultSection();
    if (!resultSection) return;

    resultSection.innerHTML = `
        <div class="alert alert-success">
            <div class="d-flex justify-content-between align-items-center">
                <strong>Generated Passphrase:</strong>
                <button class="btn btn-sm btn-outline-success copy-btn" data-target="passphrase">Copy</button>
            </div>
            <pre id="passphrase" class="mt-2 mb-0">${passphrase}</pre>
        </div>
    `;

    // Add click handler for copy button
    const copyBtn = resultSection.querySelector('.copy-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            copyToClipboard('passphrase');
        });
    }
}

// Update PGP Key Options to match backend
export const PGP_KEY_OPTIONS = {
    RSA: {
        lengths: [2048, 4096],
        defaultLength: 2048
    }
};
