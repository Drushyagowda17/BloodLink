// Global variables
let currentLanguage = 'en';
let translations = {};
let dashboardStatsInterval;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    initializeLanguage();
    initializeChatbot();
    initializeFileUpload();
    initializeFormValidation();
    initializeDashboardStats();
    initializeAnimations();
    initializeAccessibility();
});

// Theme Management with Enhanced Dark Mode
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
    
    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
        metaThemeColor.setAttribute('content', theme === 'dark' ? '#1a1a1a' : '#ffffff');
    }
    
    // Trigger custom event for theme change
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    
    // Add smooth transition effect
    document.body.style.transition = 'all 0.3s ease-in-out';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);
}

// Enhanced Language Management
function initializeLanguage() {
    const savedLanguage = localStorage.getItem('language') || 'en';
    changeLanguage(savedLanguage);
    
    // Add language change listeners
    const languageButtons = document.querySelectorAll('[data-lang]');
    languageButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const lang = button.getAttribute('data-lang');
            changeLanguage(lang);
        });
    });
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
            
            // Update HTML lang attribute
            document.documentElement.lang = lang;
            
            // Trigger custom event for language change
            window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
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
            } else if (element.tagName === 'TEXTAREA' && element.hasAttribute('placeholder')) {
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

// Enhanced Chatbot Management
function initializeChatbot() {
    const chatbotInput = document.getElementById('chatbotInput');
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Auto-resize textarea
    if (chatbotInput && chatbotInput.tagName === 'TEXTAREA') {
        chatbotInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
    
    // Initialize draggable functionality
    initializeChatbotDragging();
}

// Draggable Chatbot Functionality
function initializeChatbotDragging() {
    const chatbotWidget = document.getElementById('chatbotWidget');
    const chatbotToggleBtn = document.getElementById('chatbotToggleBtn');
    const chatbotHeader = document.querySelector('.chatbot-header');
    
    if (!chatbotWidget || !chatbotToggleBtn) return;
    
    let isDragging = false;
    let dragOffset = { x: 0, y: 0 };
    let startPos = { x: 0, y: 0 };
    let hasMoved = false;
    let dragTarget = null;
    
    // Mouse events for toggle button
    chatbotToggleBtn.addEventListener('mousedown', startDrag);
    
    // Mouse events for header (when panel is open)
    if (chatbotHeader) {
        chatbotHeader.addEventListener('mousedown', startDragFromHeader);
    }
    
    // Global mouse events
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', endDrag);
    
    // Touch events for toggle button
    chatbotToggleBtn.addEventListener('touchstart', startDragTouch, { passive: false });
    
    // Touch events for header
    if (chatbotHeader) {
        chatbotHeader.addEventListener('touchstart', startDragTouchFromHeader, { passive: false });
    }
    
    // Global touch events
    document.addEventListener('touchmove', dragTouch, { passive: false });
    document.addEventListener('touchend', endDragTouch);
    
    function startDrag(e) {
        isDragging = true;
        hasMoved = false;
        dragTarget = 'button';
        chatbotWidget.classList.add('dragging');
        
        const rect = chatbotWidget.getBoundingClientRect();
        dragOffset.x = e.clientX - rect.left;
        dragOffset.y = e.clientY - rect.top;
        startPos.x = e.clientX;
        startPos.y = e.clientY;
        
        e.preventDefault();
    }
    
    function startDragFromHeader(e) {
        // Don't drag if clicking on close button
        if (e.target.closest('.chatbot-close-btn')) {
            return;
        }
        
        isDragging = true;
        hasMoved = false;
        dragTarget = 'header';
        chatbotWidget.classList.add('dragging');
        
        const rect = chatbotWidget.getBoundingClientRect();
        dragOffset.x = e.clientX - rect.left;
        dragOffset.y = e.clientY - rect.top;
        startPos.x = e.clientX;
        startPos.y = e.clientY;
        
        e.preventDefault();
    }
    
    function startDragTouch(e) {
        const touch = e.touches[0];
        isDragging = true;
        hasMoved = false;
        dragTarget = 'button';
        chatbotWidget.classList.add('dragging');
        
        const rect = chatbotWidget.getBoundingClientRect();
        dragOffset.x = touch.clientX - rect.left;
        dragOffset.y = touch.clientY - rect.top;
        startPos.x = touch.clientX;
        startPos.y = touch.clientY;
        
        e.preventDefault();
    }
    
    function startDragTouchFromHeader(e) {
        // Don't drag if touching close button
        if (e.target.closest('.chatbot-close-btn')) {
            return;
        }
        
        const touch = e.touches[0];
        isDragging = true;
        hasMoved = false;
        dragTarget = 'header';
        chatbotWidget.classList.add('dragging');
        
        const rect = chatbotWidget.getBoundingClientRect();
        dragOffset.x = touch.clientX - rect.left;
        dragOffset.y = touch.clientY - rect.top;
        startPos.x = touch.clientX;
        startPos.y = touch.clientY;
        
        e.preventDefault();
    }
    
    function drag(e) {
        if (!isDragging) return;
        
        const moveDistance = Math.abs(e.clientX - startPos.x) + Math.abs(e.clientY - startPos.y);
        if (moveDistance > 5) {
            hasMoved = true;
        }
        
        const x = e.clientX - dragOffset.x;
        const y = e.clientY - dragOffset.y;
        
        // Keep chatbot within viewport bounds
        const maxX = window.innerWidth - chatbotWidget.offsetWidth;
        const maxY = window.innerHeight - chatbotWidget.offsetHeight;
        
        const constrainedX = Math.max(0, Math.min(x, maxX));
        const constrainedY = Math.max(0, Math.min(y, maxY));
        
        chatbotWidget.style.left = constrainedX + 'px';
        chatbotWidget.style.top = constrainedY + 'px';
        chatbotWidget.style.right = 'auto';
        chatbotWidget.style.bottom = 'auto';
        
        e.preventDefault();
    }
    
    function dragTouch(e) {
        if (!isDragging) return;
        
        const touch = e.touches[0];
        const moveDistance = Math.abs(touch.clientX - startPos.x) + Math.abs(touch.clientY - startPos.y);
        if (moveDistance > 5) {
            hasMoved = true;
        }
        
        const x = touch.clientX - dragOffset.x;
        const y = touch.clientY - dragOffset.y;
        
        // Keep chatbot within viewport bounds
        const maxX = window.innerWidth - chatbotWidget.offsetWidth;
        const maxY = window.innerHeight - chatbotWidget.offsetHeight;
        
        const constrainedX = Math.max(0, Math.min(x, maxX));
        const constrainedY = Math.max(0, Math.min(y, maxY));
        
        chatbotWidget.style.left = constrainedX + 'px';
        chatbotWidget.style.top = constrainedY + 'px';
        chatbotWidget.style.right = 'auto';
        chatbotWidget.style.bottom = 'auto';
        
        e.preventDefault();
    }
    
    function endDrag(e) {
        if (!isDragging) return;
        
        isDragging = false;
        chatbotWidget.classList.remove('dragging');
        
        // If the chatbot wasn't moved significantly, treat it as a click
        if (!hasMoved) {
            toggleChatbot();
        }
        
        // Save position to localStorage
        const rect = chatbotWidget.getBoundingClientRect();
        localStorage.setItem('chatbotPosition', JSON.stringify({
            left: rect.left,
            top: rect.top
        }));
    }
    
    function endDragTouch(e) {
        if (!isDragging) return;
        
        isDragging = false;
        chatbotWidget.classList.remove('dragging');
        
        // If the chatbot wasn't moved significantly, treat it as a tap
        if (!hasMoved) {
            toggleChatbot();
        }
        
        // Save position to localStorage
        const rect = chatbotWidget.getBoundingClientRect();
        localStorage.setItem('chatbotPosition', JSON.stringify({
            left: rect.left,
            top: rect.top
        }));
    }
    
    // Restore saved position
    const savedPosition = localStorage.getItem('chatbotPosition');
    if (savedPosition) {
        try {
            const pos = JSON.parse(savedPosition);
            // Ensure position is still within viewport
            const maxX = window.innerWidth - chatbotWidget.offsetWidth;
            const maxY = window.innerHeight - chatbotWidget.offsetHeight;
            
            const constrainedX = Math.max(0, Math.min(pos.left, maxX));
            const constrainedY = Math.max(0, Math.min(pos.top, maxY));
            
            chatbotWidget.style.left = constrainedX + 'px';
            chatbotWidget.style.top = constrainedY + 'px';
            chatbotWidget.style.right = 'auto';
            chatbotWidget.style.bottom = 'auto';
        } catch (e) {
            console.log('Could not restore chatbot position');
        }
    }
    
    // Handle window resize to keep chatbot in bounds
    window.addEventListener('resize', function() {
        const rect = chatbotWidget.getBoundingClientRect();
        const maxX = window.innerWidth - chatbotWidget.offsetWidth;
        const maxY = window.innerHeight - chatbotWidget.offsetHeight;
        
        if (rect.left > maxX || rect.top > maxY) {
            const constrainedX = Math.max(0, Math.min(rect.left, maxX));
            const constrainedY = Math.max(0, Math.min(rect.top, maxY));
            
            chatbotWidget.style.left = constrainedX + 'px';
            chatbotWidget.style.top = constrainedY + 'px';
        }
    });
}

function toggleChatbot() {
    const chatbotPanel = document.getElementById('chatbotPanel');
    const chatbotToggleBtn = document.getElementById('chatbotToggleBtn');
    
    if (chatbotPanel && chatbotToggleBtn) {
        const isShowing = chatbotPanel.classList.contains('show');
        chatbotPanel.classList.toggle('show');
        
        // Update button icon
        const icon = chatbotToggleBtn.querySelector('i');
        if (icon) {
            icon.className = chatbotPanel.classList.contains('show') 
                ? 'fas fa-times' 
                : 'fas fa-robot';
        }
        
        // Focus input when opening
        if (!isShowing) {
            const input = document.getElementById('chatbotInput');
            if (input) {
                setTimeout(() => input.focus(), 300);
            }
        }
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
    input.style.height = 'auto';
    
    // Show typing indicator
    const typingIndicator = addTypingIndicator();
    
    try {
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                context: {
                    language: currentLanguage,
                    timestamp: new Date().toISOString()
                }
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            // Remove typing indicator
            typingIndicator.remove();
            // Add bot response with typing effect
            addMessageToChat(data.reply, 'bot', true);
        } else {
            throw new Error('Failed to get response');
        }
    } catch (error) {
        console.error('Chatbot error:', error);
        // Remove typing indicator
        typingIndicator.remove();
        // Add error message
        addMessageToChat(translations.chatbot_error || 'Sorry, I\'m having trouble responding right now. Please try again later.', 'bot');
    }
}

function addMessageToChat(message, sender, typeEffect = false) {
    const messagesContainer = document.getElementById('chatbotMessages');
    if (!messagesContainer) return null;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'user' ? 'user-message' : 'bot-message';
    
    if (typeEffect && sender === 'bot') {
        messageDiv.textContent = '';
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        
        // Typing effect
        let i = 0;
        const typeInterval = setInterval(() => {
            messageDiv.textContent += message.charAt(i);
            i++;
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            if (i >= message.length) {
                clearInterval(typeInterval);
            }
        }, 30);
    } else {
        messageDiv.textContent = message;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    return messageDiv;
}

function addTypingIndicator() {
    const messagesContainer = document.getElementById('chatbotMessages');
    if (!messagesContainer) return null;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'bot-message typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return typingDiv;
}

// File Upload Enhancement
function initializeFileUpload() {
    const fileInput = document.getElementById('blood_report');
    const uploadArea = document.querySelector('.file-upload-area');
    
    if (fileInput && uploadArea) {
        // Drag and drop functionality
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });
        
        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }
}

function handleFileSelect(file) {
    const uploadArea = document.querySelector('.file-upload-area');
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    if (!allowedTypes.includes(file.type)) {
        showToast(translations.invalid_file_type || 'Please select a PNG, JPG, or PDF file.', 'error');
        return;
    }
    
    if (file.size > maxSize) {
        showToast(translations.file_too_large || 'File size must be less than 16MB.', 'error');
        return;
    }
    
    // Update upload area display
    if (uploadArea) {
        uploadArea.innerHTML = `
            <div class="file-selected">
                <i class="fas fa-file-${file.type.includes('pdf') ? 'pdf' : 'image'} fa-2x text-success mb-2"></i>
                <p class="mb-1"><strong>${file.name}</strong></p>
                <p class="text-muted small">${formatFileSize(file.size)}</p>
                <button type="button" class="btn btn-outline-danger btn-sm mt-2" onclick="clearFileSelection()">
                    <i class="fas fa-times me-1"></i>Remove
                </button>
            </div>
        `;
    }
}

function clearFileSelection() {
    const fileInput = document.getElementById('blood_report');
    const uploadArea = document.querySelector('.file-upload-area');
    
    if (fileInput) {
        fileInput.value = '';
    }
    
    if (uploadArea) {
        uploadArea.innerHTML = `
            <i class="fas fa-cloud-upload-alt fa-3x text-muted mb-3"></i>
            <h5 data-i18n="upload_blood_report">Upload Blood Test Report</h5>
            <p class="text-muted" data-i18n="drag_drop_or_click">Drag & drop your file here or click to browse</p>
            <small class="text-muted" data-i18n="supported_formats">Supported formats: PNG, JPG, PDF (Max 16MB)</small>
        `;
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Enhanced Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) {
                    validateField(input);
                }
            });
        });
    });
}

function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = translations.required_field || 'This field is required';
    }
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = translations.invalid_email || 'Please enter a valid email address';
        }
    }
    
    // Phone validation
    if (field.name === 'contact_number' && value) {
        const phoneRegex = /^[0-9]{10}$/;
        if (!phoneRegex.test(value.replace(/\D/g, ''))) {
            isValid = false;
            errorMessage = translations.invalid_phone || 'Please enter a valid 10-digit phone number';
        }
    }
    
    // Password validation
    if (field.type === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            errorMessage = translations.password_too_short || 'Password must be at least 6 characters long';
        }
    }
    
    // Age validation
    if (field.name === 'age' && value) {
        const age = parseInt(value);
        if (age < 18 || age > 65) {
            isValid = false;
            errorMessage = translations.invalid_age || 'Age must be between 18 and 65';
        }
    }
    
    // Update field appearance
    field.classList.toggle('is-valid', isValid);
    field.classList.toggle('is-invalid', !isValid);
    
    // Show/hide error message
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    errorDiv.textContent = errorMessage;
    
    return isValid;
}

// Dashboard Stats with Real-time Updates
function initializeDashboardStats() {
    if (document.getElementById('dashboardStats')) {
        updateDashboardStats();
        // Update stats every 30 seconds
        dashboardStatsInterval = setInterval(updateDashboardStats, 30000);
    }
}

async function updateDashboardStats() {
    try {
        const response = await fetch('/api/dashboard_stats');
        if (response.ok) {
            const stats = await response.json();
            updateStatsDisplay(stats);
        }
    } catch (error) {
        console.error('Error updating dashboard stats:', error);
    }
}

function updateStatsDisplay(stats) {
    Object.keys(stats).forEach(key => {
        const element = document.getElementById(`stat-${key}`);
        if (element) {
            const currentValue = parseInt(element.textContent) || 0;
            const newValue = stats[key];
            
            if (currentValue !== newValue) {
                animateNumber(element, currentValue, newValue);
            }
        }
    });
}

function animateNumber(element, start, end) {
    const duration = 1000;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.round(start + (end - start) * easeOutCubic(progress));
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
}

// Enhanced Animations and Interactions
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.feature-card, .stats-card, .card');
    animateElements.forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });
    
    // Add hover effects to interactive elements
    const interactiveElements = document.querySelectorAll('.btn, .card, .nav-link');
    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        el.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
}

// Accessibility Enhancements
function initializeAccessibility() {
    // Skip to main content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'skip-link sr-only';
    skipLink.textContent = 'Skip to main content';
    skipLink.addEventListener('focus', function() {
        this.classList.remove('sr-only');
    });
    skipLink.addEventListener('blur', function() {
        this.classList.add('sr-only');
    });
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Announce theme changes to screen readers
    window.addEventListener('themeChanged', function(e) {
        announceToScreenReader(`Theme changed to ${e.detail.theme} mode`);
    });
    
    // Announce language changes to screen readers
    window.addEventListener('languageChanged', function(e) {
        announceToScreenReader(`Language changed to ${e.detail.language}`);
    });
    
    // Focus management for modals
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            const firstInput = this.querySelector('input, button, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    });
}

function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

// Search functionality for hospital dashboard
function performSearch() {
    const form = document.getElementById('searchForm');
    if (form) {
        // Add loading state
        const searchBtn = form.querySelector('button[type="submit"]');
        if (searchBtn) {
            const originalText = searchBtn.innerHTML;
            searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Searching...';
            searchBtn.disabled = true;
            
            setTimeout(() => {
                form.submit();
            }, 500);
        } else {
            form.submit();
        }
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

// Enhanced Toast Notifications
function showToast(message, type = 'info', duration = 5000) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const toastId = 'toast-' + Date.now();
    toast.id = toastId;
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${getToastIcon(type)} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add to page
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast, { delay: duration });
    bsToast.show();
    
    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    });
    
    return toastId;
}

function getToastIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'danger': 'exclamation-circle'
    };
    return icons[type] || 'info-circle';
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
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

// Keyboard navigation support
document.addEventListener('keydown', function(e) {
    // ESC key to close chatbot
    if (e.key === 'Escape') {
        const chatbotPanel = document.getElementById('chatbotPanel');
        if (chatbotPanel && chatbotPanel.classList.contains('show')) {
            toggleChatbot();
        }
        
        // Close any open modals
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }
    
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[name="city"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Ctrl/Cmd + D to toggle dark mode
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        toggleTheme();
    }
});

// Print functionality
function printPage() {
    window.print();
}

// Report removal functionality
async function removeReport() {
    if (confirm(translations.confirm_remove_report || 'Are you sure you want to remove your blood test report?')) {
        try {
            const response = await fetch('/remove_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            });
            
            if (response.ok) {
                showToast(translations.report_removed || 'Blood test report removed successfully!', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                throw new Error('Failed to remove report');
            }
        } catch (error) {
            console.error('Error removing report:', error);
            showToast(translations.error_removing_report || 'Error removing report. Please try again.', 'error');
        }
    }
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString(currentLanguage === 'en' ? 'en-US' : 'en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString(currentLanguage === 'en' ? 'en-US' : 'en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export data functionality
function exportData(format = 'csv') {
    const table = document.querySelector('.table');
    if (!table) {
        showToast('No data to export', 'warning');
        return;
    }
    
    if (format === 'csv') {
        exportToCSV(table);
    } else if (format === 'json') {
        exportToJSON(table);
    }
}

function exportToCSV(table) {
    const rows = Array.from(table.querySelectorAll('tr'));
    const csv = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('th, td'));
        return cells.map(cell => `"${cell.textContent.trim()}"`).join(',');
    }).join('\n');
    
    downloadFile(csv, 'bloodlink-data.csv', 'text/csv');
}

function exportToJSON(table) {
    const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim());
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    
    const data = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('td'));
        const rowData = {};
        headers.forEach((header, index) => {
            if (cells[index]) {
                rowData[header] = cells[index].textContent.trim();
            }
        });
        return rowData;
    });
    
    downloadFile(JSON.stringify(data, null, 2), 'bloodlink-data.json', 'application/json');
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showToast(`Data exported as ${filename}`, 'success');
}

// Cleanup function
window.addEventListener('beforeunload', function() {
    if (dashboardStatsInterval) {
        clearInterval(dashboardStatsInterval);
    }
});

// Service Worker Registration for PWA capabilities
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Add CSS for animations
const animationStyles = `
    .animate-on-scroll {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease-out;
    }
    
    .animate-on-scroll.animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
        align-items: center;
    }
    
    .typing-dots span {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: currentColor;
        opacity: 0.4;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { opacity: 0.4; transform: scale(1); }
        40% { opacity: 1; transform: scale(1.2); }
    }
    
    .skip-link {
        position: absolute;
        top: -40px;
        left: 6px;
        background: var(--brand-primary);
        color: white;
        padding: 8px;
        text-decoration: none;
        border-radius: 4px;
        z-index: 10000;
        transition: top 0.3s;
    }
    
    .skip-link:focus {
        top: 6px;
    }
`;

// Inject animation styles
const styleSheet = document.createElement('style');
styleSheet.textContent = animationStyles;
document.head.appendChild(styleSheet);