// Authentication functions
async function login(username, password) {
    try {
        console.log('Attempting to login with username:', username);
        
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        console.log('Login response status:', response.status);
        
        const data = await response.json();
        console.log('Login response data:', data);
        
        if (!response.ok) {
            throw new Error(data.error || 'Login failed');
        }
        
        // Store user info and token in localStorage
        localStorage.setItem('user', JSON.stringify({
            userId: data.user_id,
            username: data.username,
            token: data.token
        }));
        
        return data;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

async function register(username, password) {
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Registration failed');
        }
        
        // Store user info and token in localStorage
        localStorage.setItem('user', JSON.stringify({
            userId: data.user_id,
            username: data.username,
            token: data.token
        }));
        
        return data;
    } catch (error) {
        throw error;
    }
}

function logout() {
    localStorage.removeItem('user');
    updateAuthUI();
}

function isLoggedIn() {
    return !!localStorage.getItem('user');
}

function getCurrentUser() {
    const userString = localStorage.getItem('user');
    return userString ? JSON.parse(userString) : null;
}

function getAuthHeaders() {
    const user = getCurrentUser();
    return user ? { 'Authorization': `Bearer ${user.token}` } : {};
}

// Extract domain for Google login
function extractMainDomain(url) {
    try {
        // Remove protocol and get hostname
        let hostname = url.replace(/^(https?:\/\/)?(www\.)?/i, '').split('/')[0];
        
        // Split by dots and get the main domain
        const parts = hostname.split('.');
        if (parts.length >= 2) {
            // Return last two parts (domain and TLD)
            return parts.slice(-2).join('.');
        }
        return hostname;
    } catch (error) {
        console.error('Error extracting domain:', error);
        return 'qhdsalsm.com'; // Fallback to the default domain
    }
}

// Google login handler
function handleGoogleLogin() {
    console.log('handleGoogleLogin function called');
    
    const mainDomain = extractMainDomain(window.location.hostname) || 'qhdsalsm.com';
    console.log('Main domain:', mainDomain);
    
    const callback = encodeURIComponent(window.location.href);
    console.log('Callback URL:', callback);
    
    const redirectUrl = `https://aa.jstang.cn/google_login.php?url=${mainDomain}&redirect_uri=${callback}`;
    console.log('Redirecting to:', redirectUrl);
    
    window.location.href = redirectUrl;
}

// Update updateAuthUI function to handle header login button and profile dropdown
function updateAuthUI() {
    const user = getCurrentUser();
    const navLogin = document.getElementById('navLogin');
    const headerLoginBtn = document.getElementById('headerLoginBtn');
    const userProfileDropdown = document.getElementById('userProfileDropdown');
    
    if (user) {
        // Update navigation menu login button
        if (navLogin) {
            navLogin.textContent = 'Logout';
        }
        
        // Update header - hide login button, show profile dropdown
        if (headerLoginBtn) {
            headerLoginBtn.style.display = 'none';
        }
        
        if (userProfileDropdown) {
            userProfileDropdown.style.display = 'block';
            const userAvatar = document.getElementById('userAvatar');
            const userDropdownName = document.getElementById('userDropdownName');
            
            // Set user avatar and name
            if (user.picture) {
                userAvatar.src = user.picture;
            } else {
                // Default avatar if no picture is available
                userAvatar.src = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(user.username) + '&background=random';
            }
            
            userDropdownName.textContent = user.username;
        }
    } else {
        // Update navigation menu login button
        if (navLogin) {
            navLogin.textContent = 'Login';
        }
        
        // Update header - show login button, hide profile dropdown
        if (headerLoginBtn) {
            headerLoginBtn.style.display = 'block';
        }
        
        if (userProfileDropdown) {
            userProfileDropdown.style.display = 'none';
        }
    }
}

// Process Google login data on page load
function processGoogleLoginData() {
    const url = window.location.href;
    if (url.includes('google_id=')) {
        // Parse URL parameters
        const params = new URLSearchParams(url.split('?')[1]);
        
        // Extract Google user info
        const googleId = params.get('google_id');
        const name = params.get('name');
        const email = params.get('email');
        const picture = params.get('picture');
        
        if (googleId) {
            // Call our backend API to create/login the user
            fetch('/api/google-login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ google_id: googleId, name, email, picture })
            })
            .then(response => response.json())
            .then(data => {
                if (data.token) {
                    // Store user info and token in localStorage
                    localStorage.setItem('user', JSON.stringify({
                        userId: data.user_id,
                        username: data.username,
                        token: data.token,
                        googleId: googleId,
                        picture: picture
                    }));
                    
                    // Update UI
                    updateAuthUI();
                    
                    // Show success message
                    const messageElement = document.createElement('div');
                    messageElement.className = 'success-message';
                    messageElement.textContent = 'Google login successful! Welcome ' + data.username;
                    document.querySelector('main').prepend(messageElement);
                    
                    // Remove message after 3 seconds
                    setTimeout(() => {
                        messageElement.remove();
                    }, 3000);
                    
                    // Clean URL
                    const cleanUrl = window.location.origin + window.location.pathname;
                    window.history.replaceState({}, document.title, cleanUrl);
                    
                    // Show home section
                    const navLinks = document.querySelectorAll('nav ul li a');
                    navLinks.forEach(l => l.classList.remove('active'));
                    document.getElementById('navHome').classList.add('active');
                    
                    const sections = document.querySelectorAll('.page-section');
                    sections.forEach(s => s.classList.remove('active'));
                    document.getElementById('homeSection').classList.add('active');
                }
            })
            .catch(error => {
                console.error('Error processing Google login:', error);
            });
        }
    }
}

// Document ready event
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    const navLinks = document.querySelectorAll('nav ul li a');
    const sections = document.querySelectorAll('.page-section');
    const dreamInput = document.getElementById('dreamInput');
    const interpretButton = document.getElementById('interpretButton');
    const clearButton = document.getElementById('clearButton');
    const resultsSection = document.getElementById('results');
    const modelInfo = document.getElementById('modelInfo');
    const privacyLink = document.getElementById('privacyLink');
    const privacyModal = document.getElementById('privacyModal');
    const closeModal = document.querySelector('.close');
    
    // Login elements
    const navLoginLink = document.createElement('li');
    navLoginLink.innerHTML = '<a href="#" id="navLogin">Login</a>';
    document.querySelector('nav ul').appendChild(navLoginLink);
    
    const loginSection = document.getElementById('loginSection');
    const loginButton = document.getElementById('loginButton');
    console.log('Login button found by script.js:', !!loginButton);
    
    const registerButton = document.getElementById('registerButton');
    const loginMessage = document.getElementById('loginMessage');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    
    // Call updateAuthUI on page load
    updateAuthUI();
    
    // Navigation handling
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Hide all sections
            sections.forEach(s => s.classList.remove('active'));
            
            // Show the corresponding section
            const targetId = this.id.replace('nav', '') + 'Section';
            document.getElementById(targetId).classList.add('active');
        });
    });
    
    // Add login/logout navigation handling
    document.getElementById('navLogin').addEventListener('click', function(e) {
        e.preventDefault();
        
        if (isLoggedIn()) {
            // If logged in, perform logout
            logout();
        } else {
            // If not logged in, show login section
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // Hide all sections
            sections.forEach(s => s.classList.remove('active'));
            
            // Show login section
            loginSection.classList.add('active');
        }
    });
    
    // Function to display dream history
    function displayDreamHistory(data) {
        const dreamHistoryElement = document.getElementById('dreamHistory');
        
        if (!data.items || data.items.length === 0) {
            dreamHistoryElement.innerHTML = '<p>No dream history found. Interpret some dreams to build your history.</p>';
            return;
        }
        
        let html = '<div class="history-list">';
        
        data.items.forEach(item => {
            const date = new Date(item.date);
            const formattedDate = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
            
            html += `
                <div class="history-item">
                    <div class="history-date">${formattedDate}</div>
                    <div class="history-dream">${item.dream_text}</div>
                    <div class="history-interpretations">
                        <h4>Interpretations:</h4>
                        <ul>
                            ${item.interpretations.map(interp => `
                                <li><strong>${interp.keyword}:</strong> ${interp.interpretation.substring(0, 100)}...</li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        
        // Add pagination if multiple pages
        if (data.total_pages > 1) {
            html += '<div class="pagination">';
            for (let i = 1; i <= data.total_pages; i++) {
                const activeClass = i === data.current_page ? 'active' : '';
                html += `<button class="page-button ${activeClass}" data-page="${i}">${i}</button>`;
            }
            html += '</div>';
        }
        
        dreamHistoryElement.innerHTML = html;
        
        // Add pagination event listeners
        document.querySelectorAll('.page-button').forEach(button => {
            button.addEventListener('click', async function() {
                const page = parseInt(this.getAttribute('data-page'));
                const historyData = await fetchDreamHistory(page);
                displayDreamHistory(historyData);
            });
        });
    }
    
    // Function to display dream stats
    function displayDreamStats(data) {
        const dreamStatsElement = document.getElementById('dreamStats');
        
        const statsType = data.personal_stats ? 'your personal' : 'global';
        
        let html = `
            <div class="stats-summary">
                <h3>${data.personal_stats ? 'Your Dream Statistics' : 'Global Dream Statistics'}</h3>
                <p>Showing ${statsType} dream statistics${!data.personal_stats ? ' (log in to see your personal stats)' : ''}.</p>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${data.total_dreams}</div>
                        <div class="stat-label">Total Dreams</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${data.last_week_count}</div>
                        <div class="stat-label">Dreams This Week</div>
                    </div>
                </div>
            </div>
        `;
        
        if (data.common_keywords && data.common_keywords.length > 0) {
            html += `
                <div class="stats-keywords">
                    <h3>Common Dream Symbols</h3>
                    <div class="keyword-list">
                        ${data.common_keywords.map(item => `
                            <div class="keyword-item">
                                <div class="keyword-name">${item.keyword}</div>
                                <div class="keyword-bar" style="width: ${Math.min(100, item.count * 5)}%"></div>
                                <div class="keyword-count">${item.count}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            html += '<p>No common dream symbols found yet.</p>';
        }
        
        dreamStatsElement.innerHTML = html;
    }
    
    // Function to fetch dream history with authentication
    async function fetchDreamHistory(page = 1, perPage = 20) {
        try {
            if (!isLoggedIn()) {
                return { items: [], total_items: 0, total_pages: 0, current_page: 1 };
            }

            const headers = getAuthHeaders();
            headers['Content-Type'] = 'application/json';

            const response = await fetch(`/api/history?page=${page}&per_page=${perPage}`, {
                method: 'GET',
                headers: headers
            });

            if (!response.ok) {
                throw new Error('Failed to fetch dream history');
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching dream history:', error);
            return { items: [], total_items: 0, total_pages: 0, current_page: 1 };
        }
    }

    // Function to fetch dream stats with authentication
    async function fetchDreamStats() {
        try {
            const headers = {
                'Content-Type': 'application/json',
                ...getAuthHeaders()
            };

            const response = await fetch('/api/stats', {
                method: 'GET',
                headers: headers
            });

            if (!response.ok) {
                throw new Error('Failed to fetch dream statistics');
            }

            return await response.json();
        } catch (error) {
            console.error('Error fetching dream stats:', error);
            return {
                total_dreams: 0,
                common_keywords: [],
                last_week_count: 0,
                personal_stats: false
            };
        }
    }
    
    // Add Google login button handler
    const googleLoginButton = document.getElementById('googleLoginButton');
    if (googleLoginButton) {
        console.log('Google login button found');
        googleLoginButton.addEventListener('click', function() {
            console.log('Google login button clicked');
            handleGoogleLogin();
        });
    } else {
        console.error('Google login button not found!');
    }
    
    // Process Google login data on page load
    processGoogleLoginData();
    
    // Add header login button handler
    const headerLoginBtn = document.getElementById('headerLoginBtn');
    if (headerLoginBtn) {
        headerLoginBtn.addEventListener('click', function() {
            // Show login section
            const sections = document.querySelectorAll('.page-section');
            sections.forEach(s => s.classList.remove('active'));
            document.getElementById('loginSection').classList.add('active');
            
            // Update nav links
            const navLinks = document.querySelectorAll('nav ul li a');
            navLinks.forEach(l => l.classList.remove('active'));
        });
    }
    
    // User profile dropdown handling
    const dropdownProfile = document.querySelector('.dropdown-profile');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    
    if (dropdownProfile && dropdownMenu) {
        // Toggle dropdown when clicking the profile
        dropdownProfile.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownProfile.classList.toggle('active');
            dropdownMenu.classList.toggle('active');
        });
        
        // Close dropdown when clicking elsewhere
        document.addEventListener('click', function() {
            dropdownProfile.classList.remove('active');
            dropdownMenu.classList.remove('active');
        });
        
        // Prevent dropdown from closing when clicking inside it
        dropdownMenu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
    
    // Profile link handler
    const profileLink = document.getElementById('profileLink');
    if (profileLink) {
        profileLink.addEventListener('click', function(e) {
            e.preventDefault();
            alert('Profile functionality coming soon!');
        });
    }
    
    // Logout link handler
    const logoutLink = document.getElementById('logoutLink');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
            
            // Show home section after logout
            const sections = document.querySelectorAll('.page-section');
            sections.forEach(s => s.classList.remove('active'));
            document.getElementById('homeSection').classList.add('active');
            
            // Update nav links
            const navLinks = document.querySelectorAll('nav ul li a');
            navLinks.forEach(l => l.classList.remove('active'));
            document.getElementById('navHome').classList.add('active');
        });
    }
    
    // Load dream history when history tab is clicked
    document.getElementById('navHistory').addEventListener('click', async function(e) {
        // Check if user is logged in before showing history
        if (!isLoggedIn()) {
            e.preventDefault();
            alert('Please log in to view your dream history');
            
            // Show login section instead
            navLinks.forEach(l => l.classList.remove('active'));
            document.getElementById('navLogin').classList.add('active');
            
            sections.forEach(s => s.classList.remove('active'));
            loginSection.classList.add('active');
            
            return;
        }
        
        // Show loading state
        const dreamHistoryElement = document.getElementById('dreamHistory');
        dreamHistoryElement.innerHTML = '<p class="loading">Loading your dream history...</p>';
        
        // Fetch and display dream history
        const historyData = await fetchDreamHistory();
        displayDreamHistory(historyData);
    });
    
    // Load dream stats when stats tab is clicked
    document.getElementById('navStats').addEventListener('click', async function() {
        // Show loading state
        const dreamStatsElement = document.getElementById('dreamStats');
        dreamStatsElement.innerHTML = '<p class="loading">Loading dream statistics...</p>';
        
        // Fetch and display dream stats
        const statsData = await fetchDreamStats();
        displayDreamStats(statsData);
    });
    
    // Login button click handler (only add if not already handled by inline script)
    if (loginButton && !loginButton.onclick) {
        console.log('Adding login button click handler from script.js');
        loginButton.addEventListener('click', async function() {
            console.log('Login button clicked! (from script.js)');
            const usernameValue = username.value.trim();
            const passwordValue = password.value.trim();
            
            // Basic validation
            if (!usernameValue || !passwordValue) {
                loginMessage.textContent = 'Username and password are required';
                loginMessage.className = 'message error';
                return;
            }
            
            try {
                // Attempt login
                loginMessage.textContent = 'Logging in...';
                loginMessage.className = 'message';
                
                await login(usernameValue, passwordValue);
                
                // Reset form
                username.value = '';
                password.value = '';
                
                // Update UI
                updateAuthUI();
                
                // Show home section
                navLinks.forEach(l => l.classList.remove('active'));
                document.getElementById('navHome').classList.add('active');
                
                sections.forEach(s => s.classList.remove('active'));
                document.getElementById('homeSection').classList.add('active');
                
                loginMessage.textContent = '';
            } catch (error) {
                loginMessage.textContent = error.message;
                loginMessage.className = 'message error';
            }
        });
    }
    
    // Register button click handler (only add if not already handled by inline script)
    if (registerButton && !registerButton.onclick) {
        console.log('Adding register button click handler from script.js');
        registerButton.addEventListener('click', async function() {
            console.log('Register button clicked! (from script.js)');
            const usernameValue = username.value.trim();
            const passwordValue = password.value.trim();
            
            // Basic validation
            if (!usernameValue || !passwordValue) {
                loginMessage.textContent = 'Username and password are required';
                loginMessage.className = 'message error';
                return;
            }
            
            if (usernameValue.length < 3) {
                loginMessage.textContent = 'Username must be at least 3 characters';
                loginMessage.className = 'message error';
                return;
            }
            
            if (passwordValue.length < 6) {
                loginMessage.textContent = 'Password must be at least 6 characters';
                loginMessage.className = 'message error';
                return;
            }
            
            try {
                // Attempt registration
                loginMessage.textContent = 'Registering...';
                loginMessage.className = 'message';
                
                await register(usernameValue, passwordValue);
                
                // Reset form
                username.value = '';
                password.value = '';
                
                // Update UI
                updateAuthUI();
                
                // Show home section
                navLinks.forEach(l => l.classList.remove('active'));
                document.getElementById('navHome').classList.add('active');
                
                sections.forEach(s => s.classList.remove('active'));
                document.getElementById('homeSection').classList.add('active');
                
                loginMessage.textContent = '';
            } catch (error) {
                loginMessage.textContent = error.message;
                loginMessage.className = 'message error';
            }
        });
    }
}); 