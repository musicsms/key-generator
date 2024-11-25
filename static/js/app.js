// Main application module
import { clearOutputs, attachTogglePassword } from './utils.js';
import { 
    handlePassphraseGeneration, 
    handleSSHKeyGeneration, 
    handleRSAKeyGeneration, 
    displayPassphrase 
} from './generators.js';

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Get form elements
    const passphraseForm = document.getElementById('passphraseForm');
    const sshForm = document.getElementById('sshForm');
    const rsaForm = document.getElementById('rsaForm');
    
    console.log('Forms found:', {
        passphraseForm: !!passphraseForm,
        sshForm: !!sshForm,
        rsaForm: !!rsaForm
    });

    // Attach event listeners
    if (passphraseForm) {
        passphraseForm.addEventListener('submit', (e) => {
            console.log('Passphrase form submitted');
            handlePassphraseGeneration(e);
        });
    }

    if (sshForm) {
        sshForm.addEventListener('submit', (e) => {
            console.log('SSH form submitted');
            handleSSHKeyGeneration(e);
        });
    }

    if (rsaForm) {
        rsaForm.addEventListener('submit', (e) => {
            console.log('RSA form submitted');
            handleRSAKeyGeneration(e);
        });
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
        
        if (!keyTypeSelect || !keySizeSelect) return;

        const selectedType = keyTypeSelect.value;
        const sizes = SSH_KEY_SIZES[selectedType] || [];

        // Clear existing options
        keySizeSelect.innerHTML = '';

        // Add new options
        sizes.forEach(size => {
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

    // Initial password toggle attachment
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
