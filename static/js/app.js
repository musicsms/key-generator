// Main application module
import { clearOutputs, attachTogglePassword, togglePasswordHandler } from './utils.js';
import { 
    handlePassphraseGeneration, 
    handleSSHKeyGeneration,
    handleRSAKeyGeneration,
    handlePGPKeyGeneration,
    PGP_KEY_OPTIONS,
    displayPassphrase 
} from './generators.js';

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Initialize password toggles
    attachTogglePassword();

    // Get form elements
    const passphraseForm = document.getElementById('passphraseForm');
    const sshForm = document.getElementById('sshForm');
    const rsaForm = document.getElementById('rsaForm');
    const pgpForm = document.getElementById('pgpForm');
    
    console.log('Forms found:', {
        passphraseForm: !!passphraseForm,
        sshForm: !!sshForm,
        rsaForm: !!rsaForm,
        pgpForm: !!pgpForm
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

    if (pgpForm) {
        pgpForm.addEventListener('submit', (e) => {
            console.log('PGP form submitted');
            handlePGPKeyGeneration(e);
        });
        
        // Initialize PGP key type options
        const keyTypeSelect = document.getElementById('pgpKeyType');
        if (keyTypeSelect) {
            keyTypeSelect.addEventListener('change', updatePGPKeyOptions);
            // Initial update of options
            updatePGPKeyOptions();
        }

        // Ensure toggle password is attached to PGP form
        const pgpPassphraseToggle = pgpForm.querySelector('.toggle-password');
        if (pgpPassphraseToggle) {
            pgpPassphraseToggle.removeEventListener('click', togglePasswordHandler);
            pgpPassphraseToggle.addEventListener('click', togglePasswordHandler);
        }
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
        // Only clear if clicking a tab or the generate buttons
        if (e.target.closest('[data-bs-toggle="tab"]') || 
            (e.target.tagName === 'BUTTON' && e.target.type === 'submit')) {
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

    // Function to update PGP key options based on key type
    function updatePGPKeyOptions() {
        const keyType = document.getElementById('pgpKeyType').value;
        const rsaOptions = document.getElementById('pgpRsaOptions');
        const eccOptions = document.getElementById('pgpEccOptions');
        
        if (!rsaOptions || !eccOptions) return;

        // Show/hide appropriate options
        if (keyType === 'RSA') {
            rsaOptions.style.display = 'block';
            eccOptions.style.display = 'none';
            
            // Update RSA key length options if not already populated
            const keyLengthSelect = document.getElementById('pgpKeyLength');
            if (keyLengthSelect && !keyLengthSelect.options.length) {
                PGP_KEY_OPTIONS.RSA.lengths.forEach(({ value, label }) => {
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = label;
                    keyLengthSelect.appendChild(option);
                });
            }
        } else {
            rsaOptions.style.display = 'none';
            eccOptions.style.display = 'block';
            
            // Update ECC curve options if not already populated
            const curveSelect = document.getElementById('pgpCurve');
            if (curveSelect && !curveSelect.options.length) {
                PGP_KEY_OPTIONS.ECC.curves.forEach(({ value, label }) => {
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = label;
                    curveSelect.appendChild(option);
                });
            }
        }
    }

    // Add event listener to key type select
    const keyTypeSelect = document.getElementById('sshKeyType');
    if (keyTypeSelect) {
        keyTypeSelect.addEventListener('change', updateSSHKeySizes);
        
        // Initial update
        updateSSHKeySizes();
    }

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
