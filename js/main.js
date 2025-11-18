// ============================
// HYTRAQ - Main JavaScript
// ============================

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    initSmoothScrolling();
    
    // Form handling
    initFormHandling();
    
    // Active navigation highlighting
    initActiveNavigation();
    
    // Use cases sidebar navigation
    initUseCasesNavigation();
    
    // ESG benefits sidebar navigation
    initESGNavigation();
});

/**
 * Initialize smooth scrolling for navigation links
 */
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Skip if it's just "#"
            if (href === '#') return;
            
            const target = document.querySelector(href);
            
            if (target) {
                e.preventDefault();
                
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Initialize form handling with validation
 */
function initFormHandling() {
    const form = document.querySelector('#demo form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const nameInput = form.querySelector('input[type="text"]');
        const emailInput = form.querySelector('input[type="email"]');
        const messageInput = form.querySelector('textarea');
        const submitButton = form.querySelector('button');
        
        // Get form values
        const name = nameInput.value.trim();
        const email = emailInput.value.trim();
        const message = messageInput.value.trim();
        
        // Remove existing messages
        const existingMessage = form.querySelector('.form-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Validation
        if (!name || !email || !message) {
            showFormMessage(form, 'Please fill in all fields.', 'error');
            return;
        }
        
        if (!isValidEmail(email)) {
            showFormMessage(form, 'Please enter a valid email address.', 'error');
            return;
        }
        
        // Disable submit button
        submitButton.disabled = true;
        submitButton.textContent = 'Sending...';
        
        // Simulate form submission
        // In production, replace this with actual API call
        setTimeout(() => {
            // For demo purposes, we'll just show success
            // In production, you would:
            // 1. Send data to your backend/API
            // 2. Handle success/error responses
            // 3. Optionally use a service like Formspree, Netlify Forms, etc.
            
            showFormMessage(form, 'Thank you! We\'ll be in touch soon.', 'success');
            form.reset();
            submitButton.disabled = false;
            submitButton.textContent = 'Submit';
            
            // Scroll to message
            const messageEl = form.querySelector('.form-message');
            if (messageEl) {
                messageEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }, 1000);
    });
}

/**
 * Show form message (success or error)
 */
function showFormMessage(form, message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `form-message ${type}`;
    messageDiv.textContent = message;
    form.appendChild(messageDiv);
    
    // Auto-remove success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Highlight active navigation item based on scroll position
 */
function initActiveNavigation() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('header nav a[href^="#"]');
    
    if (sections.length === 0 || navLinks.length === 0) return;
    
    function updateActiveNav() {
        const scrollPosition = window.pageYOffset + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }
    
    // Update on scroll
    let ticking = false;
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(function() {
                updateActiveNav();
                ticking = false;
            });
            ticking = true;
        }
    });
    
    // Initial update
    updateActiveNav();
}

/**
 * Initialize use cases sidebar navigation
 */
function initUseCasesNavigation() {
    const navItems = document.querySelectorAll('.use-cases-sidebar .nav-item');
    const sections = document.querySelectorAll('.use-case-section');
    
    if (navItems.length === 0 || sections.length === 0) return;
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            
            // Update active nav item
            navItems.forEach(n => n.classList.remove('active'));
            this.classList.add('active');
            
            // Update active section
            sections.forEach(s => {
                s.classList.remove('active');
                if (s.id === targetId) {
                    s.classList.add('active');
                    // Scroll to top of content area
                    const contentArea = document.querySelector('.use-cases-content');
                    if (contentArea) {
                        contentArea.scrollTop = 0;
                    }
                }
            });
        });
    });
}

/**
 * Initialize ESG benefits centered navigation with expandable content
 */
function initESGNavigation() {
    const navItems = document.querySelectorAll('.esg-nav-item');
    const sections = document.querySelectorAll('.esg-pillar-expandable');
    
    if (navItems.length === 0 || sections.length === 0) return;
    
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            
            // Update active nav item
            navItems.forEach(n => n.classList.remove('active'));
            this.classList.add('active');
            
            // Close all sections first
            sections.forEach(s => {
                s.classList.remove('active');
            });
            
            // Then open the selected one
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                // Small delay to allow close animation
                setTimeout(() => {
                    targetSection.classList.add('active');
                }, 100);
            }
        });
    });
}

