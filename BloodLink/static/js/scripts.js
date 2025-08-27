// Global variables
let currentLanguage = 'en';
let translations = {};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    initializeLanguage();
    initializeChatbot();
});

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
    localStorage.setItem('theme', theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

// Language Management
function initializeLanguage() {
    const savedLanguage = localStorage.getItem('language') || 'en';
    changeLanguage(savedLanguage);
}

async function changeLanguage(lang) {
    try {
        const response = await fetch(`/static/i18n/${lang}.json`);
        if (response.ok) {
            translations = await response.json();
            currentLanguage = lang;
            localStorage.setItem('language', lang);
            updatePageText();
            updateLanguageDisplay(lang);
        }
    } catch (error) {
        console.error('Error loading language file:', error);
        // Fallback to English if language file fails to load
        if (lang !== 'en') {
            changeLanguage('en');
        }
    }
}

function updatePageText() {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[key]) {
            if (element.tagName === 'INPUT' && element.type === 'submit') {
                element.value = translations[key];
            } else if (element.tagName === 'INPUT' && element.hasAttribute('placeholder')) {
                element.placeholder = translations[key];
            } else {
                element.textContent = translations[key];
            }
        }
    });
}

function updateLanguageDisplay(lang) {
    const currentLangElement = document.getElementById('currentLang');
    if (currentLangElement) {
        const langMap = {
            'en': 'EN',
            'kn': 'ಕನ್ನಡ',
            'hi': 'हिं'
        };
        currentLangElement.textContent = langMap[lang] || 'EN';
    }
}

// Chatbot Management
function initializeChatbot() {
    const chatbotInput = document.getElementById('chatbotInput');
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

function toggleChatbot() {
    const chatbotBody = document.getElementById('chatbotBody');
    const chatbotToggle = document.getElementById('chatbotToggle');
    
    if (chatbotBody && chatbotToggle) {
        chatbotBody.classList.toggle('show');
        chatbotToggle.className = chatbotBody.classList.contains('show') 
            ? 'fas fa-chevron-down' 
            : 'fas fa-chevron-up';
    }
}

async function sendMessage() {
    const input = document.getElementById('chatbotInput');
    const messagesContainer = document.getElementById('chatbotMessages');
    
    if (!input || !messagesContainer) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    
    // Show loading indicator
    const loadingMessage = addMessageToChat('', 'bot', true);
    
    try {
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                context: {
                    language: currentLanguage
                }
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            // Remove loading message
            loadingMessage.remove();
            // Add bot response
            addMessageToChat(data.reply, 'bot');
        } else {
            throw new Error('Failed to get response');
        }
    } catch (error) {
        console.error('Chatbot error:', error);
        // Remove loading message
        loadingMessage.remove();
        // Add error message
        addMessageToChat('Sorry, I\'m having trouble responding right now. Please try again later.', 'bot');
    }
}

function addMessageToChat(message, sender, isLoading = false) {
    const messagesContainer = document.getElementById('chatbotMessages');
    if (!messagesContainer) return null;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'user' ? 'user-message' : 'bot-message';
    
    if (isLoading) {
        messageDiv.innerHTML = '<div class="loading"></div>';
    } else {
        messageDiv.textContent = message;
    }
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageDiv;
}

// Form Validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (field.value && !emailRegex.test(field.value)) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    // Phone validation
    const phoneFields = form.querySelectorAll('input[name="contact_number"]');
    phoneFields.forEach(field => {
        const phoneRegex = /^[0-9]{10}$/;
        if (field.value && !phoneRegex.test(field.value.replace(/\D/g, ''))) {
            field.classList.add('is-invalid');
            isValid = false;
        }
    });
    
    return isValid;
}

// Search functionality for hospital dashboard
function performSearch() {
    const form = document.getElementById('searchForm');
    if (form) {
        form.submit();
    }
}

// Clear search filters
function clearSearch() {
    const searchInputs = document.querySelectorAll('#searchForm input, #searchForm select');
    searchInputs.forEach(input => {
        input.value = '';
    });
    performSearch();
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString(currentLanguage === 'en' ? 'en-US' : 'en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add to page
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Keyboard navigation support
document.addEventListener('keydown', function(e) {
    // ESC key to close chatbot
    if (e.key === 'Escape') {
        const chatbotBody = document.getElementById('chatbotBody');
        if (chatbotBody && chatbotBody.classList.contains('show')) {
            toggleChatbot();
        }
    }
    
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[name="city"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Print functionality
function printPage() {
    window.print();
}

// Export data functionality (for future use)
function exportData(format = 'csv') {
    // This would be implemented based on specific requirements
    console.log(`Exporting data in ${format} format`);
}