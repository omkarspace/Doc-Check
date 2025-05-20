// Initialize login functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeLoginForm();
    checkAuth();
});

/**
 * Initialize the login form with event listeners
 */
function initializeLoginForm() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    // Initialize password toggle
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        initPasswordToggle(passwordInput);
    }

    // Handle form submission
    loginForm.addEventListener('submit', handleLogin);
}

/**
 * Initialize password visibility toggle
 * @param {HTMLInputElement} passwordInput - The password input element
 */
function initPasswordToggle(passwordInput) {
    const passwordContainer = passwordInput.parentNode;
    passwordContainer.classList.add('relative');
    
    const togglePassword = document.createElement('button');
    togglePassword.type = 'button';
    togglePassword.className = 'absolute inset-y-0 right-0 pr-3 flex items-center';
    togglePassword.setAttribute('aria-label', 'Toggle password visibility');
    
    const eyeIcon = document.createElement('span');
    eyeIcon.innerHTML = `
        <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
            <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
        </svg>
    `;
    
    togglePassword.appendChild(eyeIcon);
    passwordContainer.appendChild(togglePassword);

    let passwordVisible = false;
    togglePassword.addEventListener('click', () => {
        passwordVisible = !passwordVisible;
        passwordInput.type = passwordVisible ? 'text' : 'password';
        
        const newEyeIcon = document.createElement('span');
        newEyeIcon.innerHTML = `
            <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                ${passwordVisible ? 
                    '<path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd" />' :
                    '<path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />' +
                    '<path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />'}
            </svg>
        `;
        
        togglePassword.replaceChild(newEyeIcon.firstChild, eyeIcon.firstChild);
        eyeIcon.innerHTML = newEyeIcon.innerHTML;
    });
}

/**
 * Handle login form submission
 * @param {Event} e - The form submission event
 */
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email')?.value.trim();
    const password = document.getElementById('password')?.value;
    const rememberMe = document.getElementById('remember-me')?.checked;
    const submitButton = e.target.querySelector('button[type="submit"]');
    const errorMessage = document.getElementById('error-message');
    const buttonText = document.getElementById('button-text');
    const buttonSpinner = document.getElementById('button-spinner');
    
    // Validate inputs
    if (!email || !password) {
        showError('Please enter both email and password', errorMessage);
        return;
    }
    
    // Disable button and show loading state
    submitButton.disabled = true;
    buttonText.textContent = 'Signing in...';
    buttonSpinner?.classList.remove('hidden');
    
    if (errorMessage) {
        errorMessage.textContent = '';
        errorMessage.classList.add('hidden');
    }
    
    try {
        // Prepare login data - using 'username' field as expected by the backend
        const loginData = {
            username: email,  // Using email as username
            password: password,
            remember_me: rememberMe
        };
        
        console.log('Sending login request with:', loginData);
        
        // Send login request as JSON
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(loginData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }
        
        // Save token to localStorage
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        
        // Save user data
        if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user));
        }
        
        // Redirect to dashboard
        window.location.href = '/dashboard';
        return { success: true, data };
    } catch (error) {
        console.error('Login error:', error);
        // Show error message
        const errorMsg = error.message || 'An error occurred during login. Please try again.';
        showError(errorMsg, errorMessage);
    } finally {
        // Re-enable button
        submitButton.disabled = false;
        buttonText.textContent = 'Sign in';
        buttonSpinner?.classList.add('hidden');
    }
}

/**
 * Display an error message to the user
 * @param {string} message - The error message to display
 * @param {HTMLElement|null} errorElement - The element to show the error in, or null to use alert()
 */
function showError(message, errorElement) {
    console.error('Login error:', message);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
        // Scroll to error message
        errorElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
        alert(message);
    }
}

/**
 * Check if user is already authenticated and redirect if needed
 */
function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (token && window.location.pathname === '/login') {
        window.location.href = '/dashboard';
    } else if (!token && !['/login', '/register'].includes(window.location.pathname)) {
        window.location.href = '/login';
    }
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
}
