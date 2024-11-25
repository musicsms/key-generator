document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Initialize password toggle buttons
    document.querySelectorAll('.toggle-password').forEach(button => {
        button.addEventListener('click', function() {
            togglePassword(this);
        });
    });

    const forms = {
        passphrase: document.getElementById('passphraseForm'),
        ssh: document.getElementById('sshForm'),
        pgp: document.getElementById('pgpForm'),
        rsa: document.getElementById('rsaForm')
    };

    // Utility Functions
    function showLoading() {
        document.querySelectorAll('button[type="submit"]').forEach(button => {
            button.disabled = true;
            const originalText = button.innerHTML;
            button.setAttribute('data-original-text', originalText);
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Loading...';
        });
    }

    function hideLoading() {
        document.querySelectorAll('button[type="submit"]').forEach(button => {
            button.disabled = false;
            button.innerHTML = button.getAttribute('data-original-text') || 'Generate';
        });
    }

    function displayMessage(message, type = 'info') {
        clearOutputs();
        const resultSection = document.getElementById('resultSection');
        const customResult = document.getElementById('customResult');
        
        resultSection.style.display = 'block';
        customResult.innerHTML = `
            <div class="alert alert-${type}" role="alert">
                ${message}
            </div>
        `;
    }

    function clearOutputs() {
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

        // Explicitly hide any visible result sections
        const resultSections = document.querySelectorAll('.result-section');
        resultSections.forEach(section => {
            section.style.display = 'none';
        });
    }

    // Handle form submissions
    Object.entries(forms).forEach(([type, form]) => {
        if (type === 'pgp') {
            form.addEventListener('submit', handlePGPForm);
        } else if (type === 'passphrase') {
            form.addEventListener('submit', handlePassphraseForm);
        } else if (type === 'ssh') {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const data = {
                    keyType: formData.get('keyType'),
                    keySize: parseInt(formData.get('keySize')),
                    passphrase: formData.get('passphrase') || null
                };

                console.log('Submitting SSH key generation:', data);
                showLoading();

                try {
                    const response = await fetch('/generate/ssh', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();
                    hideLoading();

                    console.log('SSH Key Generation Result:', result);

                    // Check for success flag
                    if (!result.success) {
                        throw new Error(result.error_message || 'Failed to generate SSH key');
                    }

                    // Extract key details from the result
                    const keyDetails = result.result;

                    // Ensure result has the expected structure
                    if (!keyDetails.publicKey || !keyDetails.privateKey) {
                        throw new Error('Invalid key generation response');
                    }

                    // Display the generated keys
                    const publicKeyElement = document.getElementById('publicKey');
                    const privateKeyElement = document.getElementById('privateKey');
                    
                    if (publicKeyElement && privateKeyElement) {
                        publicKeyElement.value = keyDetails.publicKey;
                        privateKeyElement.value = keyDetails.privateKey;
                        
                        // Show key pair result section
                        const resultSection = document.getElementById('resultSection');
                        const keyPairResult = document.getElementById('keyPairResult');
                        
                        if (resultSection) resultSection.style.display = 'block';
                        if (keyPairResult) keyPairResult.style.display = 'block';
                    }
                } catch (error) {
                    hideLoading();
                    console.error('SSH Key Generation Error:', error);
                    
                    // Display error message to user
                    const errorMessage = error.message || 'An unexpected error occurred';
                    displayMessage(errorMessage, 'danger');
                }
            });
        } else if (type === 'rsa') {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const data = Object.fromEntries(formData.entries());

                console.log('Submitting RSA key generation:', data);
                showLoading();

                try {
                    const response = await fetch('/generate/rsa', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();
                    hideLoading();

                    console.log('RSA Key Generation Result:', result);

                    // Check for success flag
                    if (!result.success) {
                        throw new Error(result.error_message || 'Failed to generate RSA key');
                    }

                    // Extract key details from the result
                    const keyDetails = result.result;

                    // Ensure result has the expected structure
                    if (!keyDetails.publicKey || !keyDetails.privateKey) {
                        throw new Error('Invalid key generation response');
                    }

                    // Display the generated keys
                    const publicKeyElement = document.getElementById('publicKey');
                    const privateKeyElement = document.getElementById('privateKey');
                    
                    if (publicKeyElement && privateKeyElement) {
                        publicKeyElement.value = keyDetails.publicKey;
                        privateKeyElement.value = keyDetails.privateKey;
                        
                        // Show key pair result section
                        const resultSection = document.getElementById('resultSection');
                        const keyPairResult = document.getElementById('keyPairResult');
                        
                        if (resultSection) resultSection.style.display = 'block';
                        if (keyPairResult) keyPairResult.style.display = 'block';
                    }
                } catch (error) {
                    hideLoading();
                    console.error('RSA Key Generation Error:', error);
                    
                    // Display error message to user
                    const errorMessage = error.message || 'An unexpected error occurred';
                    displayMessage(errorMessage, 'danger');
                }
            });
        } else {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const data = Object.fromEntries(formData.entries());

                console.log('Submitting form for:', type);
                console.log('Form data:', data);
                showLoading();

                try {
                    const response = await fetch(`/generate/${type}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();
                    hideLoading();

                    console.log('Generation Result:', result);

                    // Check for success flag
                    if (!result.success) {
                        throw new Error(result.error_message || 'Failed to generate key');
                    }

                    // Display result based on type
                    displayResult(result.result, type);
                } catch (error) {
                    hideLoading();
                    console.error('Key Generation Error:', error);
                    
                    // Display error message to user
                    const errorMessage = error.message || 'An unexpected error occurred';
                    displayMessage(errorMessage, 'danger');
                }
            });
        }
    });

    function handlePGPForm(event) {
        event.preventDefault();
        
        // Show loading state
        showLoading();

        fetch('/generate/pgp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(result => {
            hideLoading();

            // Check for success flag
            if (!result.success) {
                // Display error message
                displayMessage(result.error_message || 'Failed to generate PGP key', 'danger');
                return;
            }

            // If successful but no result (placeholder)
            displayMessage(result.result?.message || 'PGP key generation is not yet implemented', 'info');
        })
        .catch(error => {
            hideLoading();
            displayMessage('An error occurred while generating the PGP key', 'danger');
            console.error('PGP key generation error:', error);
        });
    }

    function handlePassphraseForm(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        
        // Convert form data to object and ensure boolean values
        const data = {
            length: parseInt(formData.get('length') || 16),
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
            // Hide loading state
            hideLoading();
            
            // Check if response is ok
            if (!response.ok) {
                throw new Error('Failed to generate passphrase');
            }
            return response.json();
        })
        .then(result => {
            // Display the generated passphrase
            if (result.success && result.result.passphrase) {
                displayPassphrase(result.result.passphrase);
            } else {
                throw new Error(result.error_message || 'No passphrase generated');
            }
        })
        .catch(error => {
            // Hide loading state and show error
            hideLoading();
            displayMessage(error.message || 'An error occurred while generating the passphrase', 'danger');
            console.error('Passphrase generation error:', error);
        });
    }

    function displayPassphrase(passphrase) {
        console.log('Displaying passphrase:', passphrase);
        
        // Find all potential input elements
        const possibleInputs = [
            document.getElementById('passphrase'),
            document.querySelector('#passphraseResult input'),
            document.querySelector('#resultSection input[type="text"]')
        ];
        
        // Filter out null elements
        const validInputs = possibleInputs.filter(input => input !== null);
        
        console.log('Potential passphrase inputs:', validInputs.map(input => input ? input.id : 'null'));
        
        // Set passphrase in all valid inputs
        validInputs.forEach(input => {
            console.log('Setting passphrase in input:', input.id);
            input.value = passphrase;
            input.setAttribute('value', passphrase);
        });
        
        // Show result sections
        const resultSection = document.getElementById('resultSection');
        const passphraseResult = document.getElementById('passphraseResult');
        
        if (resultSection) {
            resultSection.style.display = 'block';
            resultSection.classList.remove('d-none');
        } else {
            console.error('Result section not found');
        }
        
        if (passphraseResult) {
            passphraseResult.style.display = 'block';
            passphraseResult.classList.remove('d-none');
        } else {
            console.error('Passphrase result container not found');
        }
        
        // Log final state
        console.log('Result section display:', resultSection?.style.display);
        console.log('Passphrase result display:', passphraseResult?.style.display);
    }

    function displayResult(result, type) {
        clearOutputs();
        
        const resultSection = document.getElementById('resultSection');
        const passphraseResult = document.getElementById('passphraseResult');
        const keyPairResult = document.getElementById('keyPairResult');
        
        resultSection.style.display = 'block';
        
        if (type === 'passphrase') {
            passphraseResult.style.display = 'block';
            document.getElementById('passphrase').value = result.passphrase;
        } else {
            keyPairResult.style.display = 'block';
            document.getElementById('publicKey').value = result.publicKey;
            document.getElementById('privateKey').value = result.privateKey;
        }
    }

    function displayCustomResult(html) {
        clearOutputs();
        
        const resultSection = document.getElementById('resultSection');
        const customResult = document.getElementById('customResult');
        
        resultSection.style.display = 'block';
        customResult.innerHTML = html;
    }

    // Function to toggle password visibility
    function togglePassword(button) {
        const inputGroup = button.closest('.input-group');
        const passwordInput = inputGroup.querySelector('input');
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

    // Ensure the function is globally available
    window.togglePassword = togglePassword;

    // Ensure copyToClipboard is defined in the global scope
    window.copyToClipboard = function(elementId) {
        console.log('Attempting to copy from element:', elementId);
        
        // Check if the function is being called
        console.trace('Function call stack');
        
        const element = document.getElementById(elementId);
        if (!element) {
            console.error('Element not found:', elementId);
            alert(`Could not find element with ID: ${elementId}`);
            return;
        }

        // Determine the value to copy (works for both input and textarea)
        const textToCopy = element.value || element.textContent;
        
        if (!textToCopy) {
            console.error('No text to copy from element:', elementId);
            alert('No text available to copy');
            return;
        }

        // Use Clipboard API
        navigator.clipboard.writeText(textToCopy)
            .then(() => {
                console.log('Successfully copied to clipboard:', textToCopy);
                
                // Try multiple ways to find the copy button
                let button = null;
                
                // Try finding button in the same input group
                if (element.parentElement && element.parentElement.classList.contains('input-group')) {
                    button = element.parentElement.querySelector('button');
                }
                
                // If not found, try finding the next sibling button
                if (!button) {
                    button = element.nextElementSibling;
                }
                
                // If still not found, try finding button in the parent
                if (!button) {
                    button = element.closest('.result-container')?.querySelector('button');
                }
                
                // Perform visual feedback if button is found
                if (button) {
                    const originalHTML = button.innerHTML;
                    button.innerHTML = '<i class="bi bi-check"></i>';
                    
                    setTimeout(() => {
                        button.innerHTML = originalHTML;
                    }, 2000);
                } else {
                    console.warn('Could not find copy button for element:', elementId);
                }
            })
            .catch(err => {
                console.error('Failed to copy text:', err);
                alert('Failed to copy to clipboard. Please try again.');
            });
    };

    // SSH Key Type and Size Mapping
    const SSH_KEY_SIZES = {
        rsa: [
            { value: '2048', label: '2048 bits' },
            { value: '4096', label: '4096 bits' }
        ],
        ecdsa: [
            { value: '256', label: '256 bits' },
            { value: '384', label: '384 bits' },
            { value: '521', label: '521 bits' }
        ],
        ed25519: [
            { value: '256', label: '256 bits' }
        ]
    };

    // Function to update key size options based on key type
    function updateSSHKeySizes() {
        const keyTypeSelect = document.getElementById('sshKeyType');
        const keySizeSelect = document.getElementById('sshKeySize');
        
        // Get the currently selected key type
        const selectedKeyType = keyTypeSelect.value;
        
        // Clear existing options
        keySizeSelect.innerHTML = '';
        
        // Add new options based on key type
        SSH_KEY_SIZES[selectedKeyType].forEach(size => {
            const option = document.createElement('option');
            option.value = size.value;
            option.textContent = size.label;
            keySizeSelect.appendChild(option);
        });
    }

    // Add event listener to key type select
    const keyTypeSelect = document.getElementById('sshKeyType');
    if (keyTypeSelect) {
        keyTypeSelect.addEventListener('change', updateSSHKeySizes);
        
        // Initial update
        updateSSHKeySizes();
    }

    // Enhanced tab change listener
    const tabs = document.querySelectorAll('a[data-bs-toggle="tab"]');
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            // Clear outputs immediately when tab is clicked
            clearOutputs();
        });
    });

    // Add global click handler to ensure clearing
    document.addEventListener('click', function(e) {
        // Check if click is outside of result areas
        const resultSection = document.getElementById('resultSection');
        if (resultSection && !resultSection.contains(e.target)) {
            clearOutputs();
        }
    });

    // Reattach toggle password functionality
    function attachTogglePassword() {
        document.querySelectorAll('.toggle-password').forEach(button => {
            // Remove any existing listeners to prevent multiple attachments
            button.removeEventListener('click', togglePasswordHandler);
            button.addEventListener('click', togglePasswordHandler);
        });
    }

    function togglePasswordHandler(event) {
        const inputGroup = event.currentTarget.closest('.input-group');
        const passwordInput = inputGroup.querySelector('input');
        const icon = event.currentTarget.querySelector('i');
        
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

    // Initial attachment
    attachTogglePassword();

    // Re-attach toggle password after any dynamic content changes
    const observer = new MutationObserver((mutations) => {
        attachTogglePassword();
    });

    // Observe the entire document for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
