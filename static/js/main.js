// ================================
// THEME TOGGLE - FULLY WORKING
// ================================

const htmlElement = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

// Load saved theme from localStorage
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
}

// Apply theme
function applyTheme(theme) {
    if (theme === 'dark') {
        htmlElement.classList.add('dark');
        updateToggleButton(true);
        document.documentElement.style.colorScheme = 'dark';
    } else {
        htmlElement.classList.remove('dark');
        updateToggleButton(false);
        document.documentElement.style.colorScheme = 'light';
    }
}

// Update toggle button appearance
function updateToggleButton(isDark) {
    if (!themeToggle) return;
    
    const circle = themeToggle.querySelector('div');
    const icon = themeToggle.querySelector('i');
    
    if (isDark) {
        // Dark mode - Navy Blue
        themeToggle.classList.remove('bg-gray-300');
        themeToggle.classList.add('bg-blue-600', 'shadow-lg', 'shadow-blue-500');
        
        if (circle) {
            circle.classList.add('translate-x-6');
        }
        
        if (icon) {
            icon.classList.remove('fas-sun');
            icon.classList.add('fas-moon', 'text-yellow-300');
        }
        
        // Add glow effect to dark mode
        addGlowEffect();
    } else {
        // Light mode - Bright
        themeToggle.classList.remove('bg-blue-600', 'shadow-lg', 'shadow-blue-500');
        themeToggle.classList.add('bg-gray-300');
        
        if (circle) {
            circle.classList.remove('translate-x-6');
        }
        
        if (icon) {
            icon.classList.remove('fas-moon', 'text-yellow-300');
            icon.classList.add('fas-sun', 'text-yellow-500');
        }
        
        removeGlowEffect();
    }
}

// Add glow effect for dark mode
function addGlowEffect() {
    // Add glowing stars
    createGlowingStars();
    
    // Add background glow
    if (!document.getElementById('glowBg')) {
        const glowBg = document.createElement('style');
        glowBg.id = 'glowBg';
        glowBg.innerHTML = `
            .dark {
                position: relative;
            }
            
            .dark::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                            radial-gradient(circle at 80% 80%, rgba(147, 51, 234, 0.1) 0%, transparent 50%);
                pointer-events: none;
                z-index: 0;
            }
        `;
        document.head.appendChild(glowBg);
    }
}

// Remove glow effect for light mode
function removeGlowEffect() {
    const glowBg = document.getElementById('glowBg');
    if (glowBg) {
        glowBg.remove();
    }
    
    // Remove glowing stars
    const starsContainer = document.getElementById('starsContainer');
    if (starsContainer) {
        starsContainer.innerHTML = '';
    }
}

// Create glowing stars for dark mode
function createGlowingStars() {
    const starsContainer = document.getElementById('starsContainer');
    if (!starsContainer) return;
    
    starsContainer.innerHTML = '';
    const starCount = window.innerWidth < 768 ? 30 : 80;
    
    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star', 'glowing-star');
        
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        const size = Math.random() * 3 + 1;
        const duration = Math.random() * 3 + 2;
        const delay = Math.random() * 5;
        const brightness = Math.random() * 0.5 + 0.5;
        
        star.style.left = x + '%';
        star.style.top = y + '%';
        star.style.width = size + 'px';
        star.style.height = size + 'px';
        star.style.animationDuration = duration + 's';
        star.style.animationDelay = delay + 's';
        star.style.opacity = brightness;
        
        // Add glow effect
        star.style.boxShadow = `0 0 ${size * 2}px rgba(59, 130, 246, 0.8), 
                                0 0 ${size * 4}px rgba(147, 51, 234, 0.5)`;
        
        starsContainer.appendChild(star);
    }
}

// Toggle theme on button click
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const currentTheme = htmlElement.classList.contains('dark') ? 'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
        
        // Add animation to toggle button
        themeToggle.style.transform = 'scale(0.95)';
        setTimeout(() => {
            themeToggle.style.transform = 'scale(1)';
        }, 100);
    });
}

// Load theme on page load
document.addEventListener('DOMContentLoaded', loadTheme);

// ================================
// MOBILE MENU TOGGLE
// ================================

const mobileMenuBtn = document.getElementById('mobileMenuBtn');
const mobileMenu = document.getElementById('mobileMenu');

if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
        
        // Animate the button
        mobileMenuBtn.style.transform = mobileMenu.classList.contains('hidden') ? 'rotate(0deg)' : 'rotate(90deg)';
    });
    
    // Close menu when clicking on a link
    const menuLinks = mobileMenu.querySelectorAll('a');
    menuLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.add('hidden');
            mobileMenuBtn.style.transform = 'rotate(0deg)';
        });
    });
}

// ================================
// FLASH MESSAGE AUTO-HIDE
// ================================

document.querySelectorAll('.flash-message').forEach(message => {
    setTimeout(() => {
        message.style.opacity = '0';
        message.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            message.style.display = 'none';
        }, 300);
    }, 5000);
});

// ================================
// DROPDOWN MENU
// ================================

document.querySelectorAll('.dropdown').forEach(dropdown => {
    const button = dropdown.querySelector('button');
    const menu = dropdown.querySelector('.dropdown-menu');
    
    if (button && menu) {
        // Show on hover (desktop)
        dropdown.addEventListener('mouseenter', () => {
            menu.style.display = 'block';
            menu.style.animation = 'slideInDown 0.3s ease';
        });
        
        dropdown.addEventListener('mouseleave', () => {
            menu.style.display = 'none';
        });
        
        // Click on mobile
        button.addEventListener('click', (e) => {
            e.preventDefault();
            if (menu.style.display === 'block') {
                menu.style.display = 'none';
            } else {
                menu.style.display = 'block';
            }
        });
    }
});

// ================================
// TWINKLE STARS EFFECT (Light Mode)
// ================================

function createTwinkleStars() {
    // Only create stars in light mode
    if (htmlElement.classList.contains('dark')) {
        return;
    }
    
    const starsContainer = document.getElementById('starsContainer');
    if (!starsContainer) return;
    
    starsContainer.innerHTML = '';
    const starCount = window.innerWidth < 768 ? 20 : 50;
    
    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        
        const x = Math.random() * 100;
        const y = Math.random() * 100;
        const size = Math.random() * 1.5 + 0.5;
        const duration = Math.random() * 2 + 1.5;
        const delay = Math.random() * 3;
        
        star.style.left = x + '%';
        star.style.top = y + '%';
        star.style.width = size + 'px';
        star.style.height = size + 'px';
        star.style.animationDuration = duration + 's';
        star.style.animationDelay = delay + 's';
        
        starsContainer.appendChild(star);
    }
}

// Create stars on page load
document.addEventListener('DOMContentLoaded', () => {
    createTwinkleStars();
});

// ================================
// SMOOTH SCROLL
// ================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});

// ================================
// ANIMATION ON SCROLL
// ================================

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate__animated', 'animate__fadeInUp');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements with data-animate attribute
document.querySelectorAll('[data-animate]').forEach(el => {
    observer.observe(el);
});

// ================================
// ACTIVE LINK HIGHLIGHT
// ================================

function highlightActiveLink() {
    const currentLocation = location.pathname;
    const menuItems = document.querySelectorAll('nav a');
    
    menuItems.forEach(item => {
        if (item.getAttribute('href') === currentLocation) {
            item.classList.add('text-navy', 'dark:text-blue-400', 'font-bold');
        } else {
            item.classList.remove('text-navy', 'dark:text-blue-400', 'font-bold');
        }
    });
}

document.addEventListener('DOMContentLoaded', highlightActiveLink);

// ================================
// PREVENT LAYOUT SHIFT
// ================================

// Add scrollbar width on page load
function updateScrollbarWidth() {
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    document.documentElement.style.setProperty('--scrollbar-width', scrollbarWidth + 'px');
}

window.addEventListener('load', updateScrollbarWidth);
window.addEventListener('resize', updateScrollbarWidth);
