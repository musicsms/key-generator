// Generation handlers for different key types
import { showLoading, hideLoading, displayMessage, clearOutputs } from './utils.js';

export function handlePassphraseGeneration(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    // Log the start of generation
    console.log('Passphrase Generation - Start', {
        formData: Object.fromEntries(formData),
        form: form
    });

    // Validate length input
    const lengthInput = form.querySelector('input[name="length"]');
    const length = parseInt(formData.get('length') || 16);
    
    // Additional client-side validation
    if (length < 8 || length > 64) {
        console.error('Invalid passphrase length:', length);
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

    // Log generation parameters
    console.log('Passphrase Generation - Parameters', data);

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
        // Log response details
        console.log('Passphrase Generation - Response', {
            status: response.status,
            ok: response.ok
        });

        // Hide loading state
        hideLoading();
        
        // Check if response is ok
        if (!response.ok) {
            console.error('Failed to generate passphrase');
            throw new Error('Failed to generate passphrase');
        }
        return response.json();
    })
    .then(result => {
        // Log generation result
        console.log('Passphrase Generation Result:', result);
        
        if (result.success) {
            // Extract passphrase from data object
            const passphrase = result.data.passphrase;
            
            // Log extracted passphrase
            console.log('Extracted Passphrase:', passphrase);
            
            // Display passphrase
            displayPassphrase(passphrase);
        } else {
            // Log generation failure
            console.error('Passphrase generation failed:', result);
            
            // Display error message
            throw new Error(result.error_message || 'No passphrase generated');
        }
    })
    .catch(error => {
        // Log any errors during generation
        console.error('Passphrase Generation Error:', error);
        
        // Hide loading state
        hideLoading();
        
        // Display error message
        displayMessage(error.message || 'An error occurred while generating the passphrase', 'danger');
    });
}

export function handleSSHKeyGeneration(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
        keyType: formData.get('keyType'),
        keySize: parseInt(formData.get('keySize')),
        passphrase: formData.get('passphrase') || null
    };

    console.log('Submitting SSH key generation:', data);
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
    })
    .catch(error => {
        hideLoading();
        console.error('SSH Key Generation Error:', error);
        
        // Display error message to user
        const errorMessage = error.message || 'An unexpected error occurred';
        displayMessage(errorMessage, 'danger');
    });
}

export function handleRSAKeyGeneration(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    // Convert form data to proper types
    const data = {
        keySize: parseInt(formData.get('keySize') || 2048),
        passphrase: formData.get('passphrase') || ''
    };

    console.log('Submitting RSA key generation:', data);
    showLoading();

    // Clear any previous outputs
    clearOutputs();

    fetch('/generate/rsa', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(async response => {
        const responseData = await response.json();
        console.log('RSA Response:', {
            status: response.status,
            ok: response.ok,
            data: responseData
        });
        
        if (!response.ok) {
            throw new Error(responseData.error_message || `HTTP error! status: ${response.status}`);
        }
        return responseData;
    })
    .then(result => {
        hideLoading();
        console.log('RSA Key Generation Result:', result);

        if (!result.success) {
            throw new Error(result.error_message || 'Failed to generate RSA key');
        }

        // Get the key pair result container
        const keyPairResult = document.getElementById('keyPairResult');
        const resultSection = document.getElementById('resultSection');

        if (!keyPairResult || !resultSection) {
            throw new Error('Result containers not found');
        }

        // Get the key elements
        const publicKeyElement = document.getElementById('publicKey');
        const privateKeyElement = document.getElementById('privateKey');

        if (!publicKeyElement || !privateKeyElement) {
            throw new Error('Key elements not found');
        }

        // Set the key values - use result.data instead of result.result
        publicKeyElement.value = result.data.publicKey;
        privateKeyElement.value = result.data.privateKey;

        // Show the results
        resultSection.style.display = 'block';
        keyPairResult.style.display = 'block';

        console.log('RSA keys displayed successfully');
    })
    .catch(error => {
        hideLoading();
        console.error('RSA Key Generation Error:', error);
        displayMessage(error.message || 'An unexpected error occurred', 'danger');
    });
}

export function displayPassphrase(passphrase) {
    console.log('displayPassphrase called with:', passphrase);
    
    // Get all elements with updated IDs
    const passphraseInput = document.getElementById('passphraseOutput');
    const passphraseResult = document.getElementById('passphraseResult');
    const resultSection = document.getElementById('resultSection');
    const passphraseTab = document.getElementById('passphrase-tab');
    const passphrasePane = document.getElementById('passphraseTab');
    
    console.log('Elements found:', {
        passphraseInput,
        passphraseResult,
        resultSection,
        passphraseTab,
        passphrasePane
    });

    // Ensure we have all required elements
    if (!passphraseInput || !passphraseResult || !resultSection) {
        console.error('Missing required elements for passphrase display');
        return;
    }

    // Make sure the passphrase tab is active
    if (passphraseTab && passphrasePane) {
        // Remove active class from all tabs and panes
        document.querySelectorAll('.nav-link').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active', 'show');
        });
        
        // Activate the passphrase tab and pane
        passphraseTab.classList.add('active');
        passphrasePane.classList.add('active', 'show');
    }

    // Set the value first
    passphraseInput.value = passphrase;
    
    // Then show the containers
    resultSection.style.display = 'block';
    passphraseResult.style.display = 'block';
    
    console.log('After setting display:', {
        inputValue: passphraseInput.value,
        resultDisplay: passphraseResult.style.display,
        sectionDisplay: resultSection.style.display,
        tabActive: passphraseTab?.classList.contains('active'),
        paneActive: passphrasePane?.classList.contains('active')
    });

    // Force a repaint
    window.requestAnimationFrame(() => {
        // Double check visibility
        resultSection.style.display = 'block';
        passphraseResult.style.display = 'block';
        
        // Log final state
        console.log('Final state:', {
            value: passphraseInput.value,
            resultDisplay: passphraseResult.style.display,
            sectionDisplay: resultSection.style.display,
            tabActive: passphraseTab?.classList.contains('active'),
            paneActive: passphrasePane?.classList.contains('active')
        });
    });
}
