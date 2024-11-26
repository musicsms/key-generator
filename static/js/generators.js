// Generation handlers for different key types
import { showLoading, hideLoading, displayMessage, clearOutputs } from './utils.js';

function validateComment(comment) {
    if (!comment) {
        throw new Error('Comment is required');
    }
    if (comment.length > 40) {
        throw new Error('Comment must be shorter than 40 characters');
    }
    if (comment.includes(' ')) {
        throw new Error('Comment cannot contain spaces, use underscores instead');
    }
    return comment;
}

export function handlePassphraseGeneration(e) {
    e.preventDefault();
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
    const form = e.target;
    const formData = new FormData(form);
    
    try {
        const comment = validateComment(formData.get('comment'));
        
        const data = {
            comment: comment,
            keyType: formData.get('keyType') || 'rsa',
            keySize: parseInt(formData.get('keySize') || 2048),
            passphrase: formData.get('passphrase') || ''
        };

        showLoading();

        fetch('/generate/ssh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            hideLoading();
            if (result.success) {
                displayMessage(`SSH key pair generated successfully in directory: ${result.data.directory}`, 'success');
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
    const form = e.target;
    const formData = new FormData(form);
    
    try {
        const comment = validateComment(formData.get('comment'));
        
        const data = {
            comment: comment,
            keySize: parseInt(formData.get('keySize') || 2048),
            passphrase: formData.get('passphrase') || ''
        };

        showLoading();

        fetch('/generate/rsa', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            hideLoading();
            if (result.success) {
                displayMessage(`RSA key pair generated successfully in directory: ${result.data.directory}`, 'success');
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

// PGP Key Type and Options Mapping
export const PGP_KEY_OPTIONS = {
    RSA: {
        lengths: [
            { value: '2048', label: '2048 bits' },
            { value: '3072', label: '3072 bits' },
            { value: '4096', label: '4096 bits' }
        ]
    },
    ECC: {
        curves: [
            { value: 'secp256k1', label: 'secp256k1' },
            { value: 'secp384r1', label: 'secp384r1' },
            { value: 'secp521r1', label: 'secp521r1' },
            { value: 'brainpoolP256r1', label: 'brainpoolP256r1' },
            { value: 'brainpoolP384r1', label: 'brainpoolP384r1' },
            { value: 'brainpoolP512r1', label: 'brainpoolP512r1' }
        ]
    }
};

export async function handlePGPKeyGeneration(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        comment: formData.get('comment') || null,
        keyType: formData.get('keyType'),
        expireTime: formData.get('expireTime')
    };

    // Add key type specific parameters
    if (data.keyType === 'RSA') {
        data.keyLength = parseInt(formData.get('keyLength'));
    } else {
        data.curve = formData.get('curve');
    }

    // Add passphrase if provided
    const passphrase = formData.get('passphrase');
    if (passphrase) {
        data.passphrase = passphrase;
    }

    console.log('Submitting PGP key generation:', data);
    showLoading();

    try {
        const response = await fetch('/generate/pgp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        hideLoading();

        if (!result.success) {
            throw new Error(result.error_message || 'Failed to generate PGP key');
        }

        // Clear any previous results
        clearOutputs();

        // Extract key data from the correct location in the response
        const keyData = result.data.message || result.data;
        if (!keyData) {
            throw new Error('Invalid response format: missing key data');
        }

        console.log('Received key data:', keyData);

        // Display the generated keys
        const publicKeyElement = document.getElementById('publicKey');
        const privateKeyElement = document.getElementById('privateKey');
        
        if (publicKeyElement && privateKeyElement) {
            publicKeyElement.value = keyData.publicKey || '';
            privateKeyElement.value = keyData.privateKey || '';
            
            // Show key pair result section
            const resultSection = document.getElementById('resultSection');
            const keyPairResult = document.getElementById('keyPairResult');
            
            if (resultSection) resultSection.style.display = 'block';
            if (keyPairResult) {
                keyPairResult.style.display = 'block';
                
                // Remove any existing additional info
                const existingInfo = keyPairResult.querySelector('.alert-info');
                if (existingInfo) {
                    existingInfo.remove();
                }

                // Add additional info
                const additionalInfo = document.createElement('div');
                additionalInfo.className = 'alert alert-info mt-3';
                additionalInfo.innerHTML = `
                    <h5>Key Details:</h5>
                    <ul class="mb-0">
                        <li>Key ID: ${keyData.keyId || 'N/A'}</li>
                        <li>Key Type: ${keyData.keyType || data.keyType}</li>
                        ${keyData.keyLength ? `<li>Key Length: ${keyData.keyLength} bits</li>` : ''}
                        ${keyData.curve ? `<li>Curve: ${keyData.curve}</li>` : ''}
                        <li>Expiration: ${keyData.expireDate || 'N/A'}</li>
                        <li>Saved in: ${keyData.directory || 'N/A'}</li>
                    </ul>
                `;
                keyPairResult.appendChild(additionalInfo);
            }
        }
    } catch (error) {
        hideLoading();
        console.error('PGP Key Generation Error:', error);
        displayMessage(error.message, 'danger');
    }
}

function displayKeys(privateKey, publicKey) {
    const resultSection = document.getElementById('resultSection');
    const keyPairResult = document.getElementById('keyPairResult');
    const privateKeyOutput = document.getElementById('privateKey');
    const publicKeyOutput = document.getElementById('publicKey');
    
    // Show the result sections
    if (resultSection) resultSection.style.display = 'block';
    if (keyPairResult) keyPairResult.style.display = 'block';
    
    // Display the keys
    if (privateKeyOutput) {
        privateKeyOutput.value = privateKey;
    }
    
    if (publicKeyOutput) {
        publicKeyOutput.value = publicKey;
    }
}

export function displayPassphrase(passphrase) {
    const resultSection = document.getElementById('resultSection');
    const passphraseResult = document.getElementById('passphraseResult');
    const passphraseOutput = document.getElementById('passphraseOutput');
    
    if (resultSection) resultSection.style.display = 'block';
    if (passphraseResult) passphraseResult.style.display = 'block';
    if (passphraseOutput) passphraseOutput.value = passphrase;
}
