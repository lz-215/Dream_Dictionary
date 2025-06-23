// Authentication functions
// The login function is now only for internal use with Google auth
async function login(userData) {
    try {
        console.log('[LOGIN] Storing user data in localStorage:', userData);
        
        // Store user info in localStorage
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Reset usage count after login
        localStorage.removeItem('usageCount');
        
        console.log('[LOGIN] User data stored successfully');
        return userData;
    } catch (error) {
        console.error('[LOGIN] Error storing user data:', error);
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
    try {
    const userString = localStorage.getItem('user');
        console.log('[GET USER] Raw user data from localStorage:', userString);
        
        if (!userString) {
            console.log('[GET USER] No user data found in localStorage');
            return null;
        }
        
        // 尝试解析JSON
        const userData = JSON.parse(userString);
        console.log('[GET USER] Parsed user data:', userData);
        return userData;
    } catch (error) {
        console.error('[GET USER] Error parsing user data:', error);
        // 发生错误时清除可能损坏的数据
        localStorage.removeItem('user');
        return null;
    }
}

function getAuthHeaders() {
    const user = getCurrentUser();
    return user ? { 'Authorization': `Bearer ${user.token}` } : {};
}

// Track usage count for non-logged-in users
function incrementUsageCount() {
    if (isLoggedIn()) return; // No need to track for logged-in users
    
    let count = parseInt(localStorage.getItem('usageCount') || '0');
    count++;
    localStorage.setItem('usageCount', count.toString());
    
    // Show login prompt after 15 uses
    if (count >= 15) {
        showLoginPrompt();
    }
}

// Show login prompt for users who have exceeded the free usage limit
function showLoginPrompt() {
    // Check if the prompt has been shown recently
    const lastPromptTime = localStorage.getItem('lastLoginPromptTime');
    const now = new Date().getTime();
    
    // Only show the prompt once per hour
    if (!lastPromptTime || (now - parseInt(lastPromptTime)) > 3600000) {
        const promptElement = document.createElement('div');
        promptElement.className = 'login-prompt';
        promptElement.innerHTML = `
            <div class="login-prompt-content">
                <i class="fas fa-info-circle"></i>
                <p>You've used 15 free interpretations. <a href="#" id="loginPromptBtn">Log in with Google</a> for unlimited free interpretations!</p>
                <button class="close-prompt"><i class="fas fa-times"></i></button>
            </div>
        `;
        
        document.querySelector('main').prepend(promptElement);
        
        // Add event listeners
        document.getElementById('loginPromptBtn').addEventListener('click', function(e) {
            e.preventDefault();
            // Hide all sections
            const sections = document.querySelectorAll('.page-section');
            sections.forEach(s => s.classList.remove('active'));
            
            // Show login section
            document.getElementById('loginSection').classList.add('active');
            
            // Remove prompt
            promptElement.remove();
        });
        
        document.querySelector('.close-prompt').addEventListener('click', function() {
            promptElement.remove();
        });
        
        // Store the time when the prompt was shown
        localStorage.setItem('lastLoginPromptTime', now.toString());
    }
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
    debugLog('Google login button clicked');
    
    // Show loading indicator on button
    const googleLoginButton = document.getElementById('googleLoginButton');
    if (googleLoginButton) {
        googleLoginButton.classList.add('loading');
    }
    
    // Get the current domain - handle both local and production environments
    let currentDomain = window.location.hostname;
    let redirectDomain;
    
    // Check if we're on localhost or an actual domain
    if (currentDomain === 'localhost' || currentDomain === '127.0.0.1') {
        // Local development - use a default domain
        redirectDomain = 'qhdsalsm.com';
    } else {
        // Production - use the actual domain without any processing
        redirectDomain = currentDomain;
    }
    
    debugLog('Using domain for redirect', redirectDomain);
    
    // Create the full callback URL - ensure it's the page URL without parameters
    const fullUrl = window.location.origin + window.location.pathname;
    const callback = encodeURIComponent(fullUrl);
    debugLog('Callback URL', callback);
    
    // Build the redirect URL for Google login - ensure we're using the current domain consistently
    const redirectUrl = `https://aa.jstang.cn/google_login.php?url=${redirectDomain}&redirect_uri=${callback}`;
    debugLog('Redirecting to', redirectUrl);
    
    try {
        // Store the last redirect attempt in local storage for debugging
        localStorage.setItem('lastGoogleRedirect', JSON.stringify({
            timestamp: new Date().toISOString(),
            domain: redirectDomain,
            callback: fullUrl,
            redirectUrl: redirectUrl
        }));
    } catch (e) {
        console.error('Error storing redirect info:', e);
    }
    
    // Add a small delay to show the loading indicator before redirecting
    setTimeout(() => {
        // Redirect to the Google login page
    window.location.href = redirectUrl;
    }, 300);
}

// Add dropdown activation functions
function initializeUserDropdown() {
    debugLog('Initializing user dropdown');
    // User profile dropdown handling
    const dropdownProfile = document.querySelector('.dropdown-profile');
    const dropdownMenu = document.querySelector('.dropdown-menu');
    if (dropdownProfile && dropdownMenu) {
        // Toggle dropdown when clicking the profile
        dropdownProfile.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownProfile.classList.toggle('active');
            dropdownMenu.classList.toggle('active');
            debugLog('User dropdown toggled');
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
        debugLog('Dropdown event listeners added');
        // 重新绑定 logout 事件，防止失效
        const logoutLink = document.getElementById('logoutLink');
        if (logoutLink) {
            logoutLink.onclick = null;
            logoutLink.addEventListener('click', function(e) {
                e.preventDefault();
                logout();
                // 切回首页
                const sections = document.querySelectorAll('.page-section');
                sections.forEach(s => s.classList.remove('active'));
                document.getElementById('homeSection').classList.add('active');
                // 更新导航
                const navLinks = document.querySelectorAll('nav ul li a');
                navLinks.forEach(l => l.classList.remove('active'));
                document.getElementById('navHome').classList.add('active');
            });
        }
    } else {
        debugLog('Dropdown elements not found', { 
            dropdownProfile: !!dropdownProfile, 
            dropdownMenu: !!dropdownMenu 
        });
    }
}

// Update updateAuthUI function to handle header login button and profile dropdown
function updateAuthUI() {
    const user = getCurrentUser();
    const navLogin = document.getElementById('navLogin');
    const headerLoginBtn = document.getElementById('headerLoginBtn');
    const userProfileDropdown = document.getElementById('userProfileDropdown');
    
    console.log('[UPDATE UI] Updating UI with user:', user);
    
    if (user) {
        // Update navigation menu login button
        if (navLogin) {
            navLogin.textContent = 'Logout';
            console.log('[UPDATE UI] Updated navLogin to Logout');
        } else {
            console.log('[UPDATE UI] navLogin element not found');
        }
        // Hide login button completely (remove from DOM)
        if (headerLoginBtn) {
            headerLoginBtn.style.display = 'none';
            // Remove the button from DOM for clean UI
            if (headerLoginBtn.parentNode) {
                headerLoginBtn.parentNode.removeChild(headerLoginBtn);
            }
            console.log('[UPDATE UI] Login button removed from DOM');
        } else {
            console.log('[UPDATE UI] headerLoginBtn element not found');
        }
        if (userProfileDropdown) {
            userProfileDropdown.style.display = 'block';
            const userAvatar = document.getElementById('userAvatar');
            if (userAvatar) {
                if (user.picture) {
                    userAvatar.src = user.picture;
                } else {
                    userAvatar.src = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(user.username) + '&background=random';
                }
            }
            // 填充邮箱
            const userEmail = document.getElementById('userEmail');
            if (userEmail && user.email) {
                userEmail.textContent = user.email;
            }
            initializeUserDropdown();
        }
    } else {
        if (navLogin) {
            navLogin.textContent = 'Login';
        }
        // 未登录时，确保按钮存在且可见
        let btn = document.getElementById('headerLoginBtn');
        if (!btn) {
            // 重新插入按钮到 .header-login-area
            const loginArea = document.querySelector('.header-login-area');
            if (loginArea) {
                btn = document.createElement('button');
                btn.id = 'headerLoginBtn';
                btn.className = 'header-login-btn';
                btn.innerHTML = '<i class="fas fa-user"></i> Login';
                loginArea.insertBefore(btn, loginArea.firstChild);
                btn.addEventListener('click', handleGoogleLogin);
            }
        } else {
            btn.style.display = 'block';
            // 防止重复绑定，先移除再绑定
            btn.onclick = null;
            btn.addEventListener('click', handleGoogleLogin);
        }
        if (userProfileDropdown) {
            userProfileDropdown.style.display = 'none';
        }
    }
}

// Process Google login data on page load
function processGoogleLoginData() {
    try {
    const url = window.location.href;
        debugLog('Checking URL for Google login data', url);
        console.log('[DEBUG] Current URL:', url);
        
        // First check if we have Google ID in the URL
    if (url.includes('google_id=')) {
            debugLog('Google ID found in URL parameters');
            console.log('[DEBUG] Google ID found in URL');
            
            // Parse URL parameters - handle both query string and hash fragment
            let params;
            if (url.includes('?google_id=')) {
                params = new URLSearchParams(window.location.search);
                debugLog('Using query string parameters');
                console.log('[DEBUG] Using query parameters');
            } else if (url.includes('#google_id=')) {
                // 处理锚点后的参数，格式如 #google_id=xxx&name=xxx
                const hashParams = url.split('#')[1];
                params = new URLSearchParams(hashParams);
                debugLog('Using hash fragment parameters', hashParams);
                console.log('[DEBUG] Using hash parameters:', hashParams);
            } else if (url.includes('/google_id=')) {
                // 处理URL中间包含/google_id=的情况
                const fullPath = url.split('/google_id=')[1];
                // 安全处理可能包含非法字符的参数
                const paramString = 'google_id=' + fullPath.replace(/[^\w\s=&%@.-]/g, '');
                params = new URLSearchParams(paramString);
                debugLog('Using embedded parameters with slash', paramString);
                console.log('[DEBUG] Using embedded parameters with slash:', paramString);
            } else if (url.includes('google_id=')) {
                // 处理URL中间包含google_id=的其他情况
                try {
                    const startIndex = url.indexOf('google_id=');
                    // 提取从google_id=开始到URL结束或下一个不允许的字符的部分
                    let endIndex = url.length;
                    const illegalChars = [' ', '"', "'", '<', '>', '\\', '{', '}'];
                    for (let char of illegalChars) {
                        const charIndex = url.indexOf(char, startIndex);
                        if (charIndex !== -1 && charIndex < endIndex) {
                            endIndex = charIndex;
                        }
                    }
                    
                    const paramString = url.substring(startIndex, endIndex);
                    debugLog('Extracted param string', paramString);
                    console.log('[DEBUG] Extracted param string:', paramString);
                    
                    // 尝试解析参数
                    params = new URLSearchParams(paramString);
                } catch (parseError) {
                    console.error('Error parsing URL parameters:', parseError);
                    debugLog('Error parsing URL parameters', parseError.message);
                    return;
                }
            } else {
                console.error('No query parameters or hash fragment found');
                return;
            }
        
        // Extract Google user info
        const googleId = params.get('google_id');
        const name = params.get('name');
        const email = params.get('email');
        const picture = params.get('picture');
            
            console.log('[DEBUG] Extracted Google info:', {
                googleId,
                name,
                email,
                picture: picture ? '(picture exists)' : '(no picture)'
            });
            
            debugLog('Extracted parameters', { 
                googleId: googleId ? googleId : 'missing', 
                name: name ? name : 'missing', 
                email: email ? email : 'missing', 
                picture: picture ? 'exists' : 'missing' 
            });
        
        if (googleId) {
                // 本地开发环境直接使用 mock 登录
                if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                    debugLog('Local environment detected, using mock login');
                    mockGoogleLogin(googleId, name, email, picture);
                    return;
                }
                
                // 生产环境 - 对于 qhdsalsm.com 域名，直接使用mock登录避免API调用
                if (window.location.hostname === 'qhdsalsm.com' || window.location.hostname === 'www.qhdsalsm.com') {
                    debugLog('qhdsalsm.com domain detected, using direct login without API');
                    mockGoogleLogin(googleId, name, email, picture);
                    return;
                }
                
                // 其他生产环境调用API
                debugLog('Calling backend API for Google login');
                
            fetch('/api/google-login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ google_id: googleId, name, email, picture })
            })
                .then(response => {
                    debugLog('API response status', response.status);
                    // 检查HTTP状态码，避免尝试解析非JSON响应
                    if (!response.ok) {
                        throw new Error(`Server responded with status: ${response.status}`);
                    }
                    
                    // 尝试安全解析JSON，处理可能的格式错误
                    return response.text().then(text => {
                        try {
                            // 首先检查文本是否为空
                            if (!text.trim()) {
                                throw new Error('Empty response from server');
                            }
                            
                            // 尝试解析JSON
                            const data = JSON.parse(text);
                            return data;
                        } catch (e) {
                            console.error('JSON parse error:', e);
                            console.log('Raw response:', text);
                            throw new Error(`Invalid JSON response: ${e.message}`);
                        }
                    });
                })
            .then(data => {
                    debugLog('API response data received');
                    
                if (data.token) {
                        // Store user info and token in localStorage using the login function
                        debugLog('Login successful, storing user data');
                        
                        const userData = {
                        userId: data.user_id,
                            username: data.username || name || email || 'User',
                        token: data.token,
                        googleId: googleId,
                        picture: picture,
                        email: email || '' // 确保包含 email 字段
                        };
                        
                        login(userData);
                    
                    // Update UI
                    updateAuthUI();
                        
                        // Force a refresh of the dropdown functionality
                        setTimeout(() => {
                            initializeUserDropdown();
                        }, 100);
                    
                    // Show success message
                    const messageElement = document.createElement('div');
                    messageElement.className = 'success-message';
                        messageElement.textContent = 'Google login successful! Welcome ' + userData.username;
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
                    } else {
                        debugLog('Login failed: Invalid response from server', data);
                        throw new Error(data.error || 'Login failed: Invalid response from server');
                }
            })
            .catch(error => {
                console.error('Error processing Google login:', error);
                    debugLog('Error processing Google login', error.message);
                    
                    // Try to use mock login for local development or on error
                    debugLog('Attempting to use mock login as fallback');
                    if (mockGoogleLogin(googleId, name, email, picture)) {
                        debugLog('Using mock login as fallback');
                        return; // Successfully used mock login
                    }
                    
                    const loginMessage = document.getElementById('loginMessage');
                    if (loginMessage) {
                        loginMessage.textContent = 'Google login failed: ' + error.message;
                        loginMessage.className = 'message error';
                    }
                });
            } else {
                console.error('Google ID not found in parameters');
                debugLog('Google ID not found in parameters');
                
                const loginMessage = document.getElementById('loginMessage');
                if (loginMessage) {
                    loginMessage.textContent = 'Google login failed: Missing required information';
                    loginMessage.className = 'message error';
                }
            }
        } else {
            debugLog('No Google login data found in URL');
        }
    } catch (error) {
        console.error('Exception in processGoogleLoginData:', error);
        debugLog('Exception in processGoogleLoginData', error.message);
    }
}

// Check for authentication errors
document.addEventListener('DOMContentLoaded', function() {
    // Check for auth errors in URL
    try {
        const url = window.location.href;
        if (url.includes('error=')) {
            let errorMessage = 'Authentication failed';
            
            // Try to parse the error message
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('error')) {
                errorMessage = urlParams.get('error');
            }
            
            // Display error message
            const loginMessage = document.getElementById('loginMessage');
            if (loginMessage) {
                loginMessage.textContent = 'Google login failed: ' + errorMessage;
                loginMessage.className = 'message error';
                
                // Show login section
                const sections = document.querySelectorAll('.page-section');
                sections.forEach(s => s.classList.remove('active'));
                document.getElementById('loginSection').classList.add('active');
            }
            
            // Clean URL
            const cleanUrl = window.location.origin + window.location.pathname;
            window.history.replaceState({}, document.title, cleanUrl);
        }
    } catch (error) {
        console.error('Error checking authentication status:', error);
    }
});

// Debug log function
function debugLog(message, data) {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || localStorage.getItem('debugMode') === 'true') {
        console.log('[DEBUG] ' + message, data || '');
    }
}

// Display debug info on the page
function showDebugInfo() {
    try {
        // Only show on local or when debug mode is enabled
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || localStorage.getItem('debugMode') === 'true') {
            const loginMessage = document.getElementById('loginMessage');
            if (loginMessage) {
                // Get last redirect info if available
                let lastRedirectInfo = '';
                try {
                    const lastRedirect = JSON.parse(localStorage.getItem('lastGoogleRedirect') || '{}');
                    if (lastRedirect.timestamp) {
                        lastRedirectInfo = `
                            <h4>Last Google Redirect</h4>
                            <p><strong>Time:</strong> ${lastRedirect.timestamp}</p>
                            <p><strong>Domain:</strong> ${lastRedirect.domain}</p>
                            <p><strong>Callback:</strong> ${lastRedirect.callback}</p>
                            <p><strong>Redirect URL:</strong> ${lastRedirect.redirectUrl}</p>
                        `;
                    }
                } catch (e) {
                    lastRedirectInfo = `<p>Error parsing last redirect: ${e.message}</p>`;
                }
                
                // 显示当前URL信息
                const currentUrlInfo = `
                    <h4>Current URL Info</h4>
                    <p><strong>Full URL:</strong> ${window.location.href}</p>
                    <div id="urlParamsInfo"></div>
                `;
                
                // 如果当前URL包含google_id参数，显示这些参数
                let googleParamsInfo = '';
                if (window.location.href.includes('google_id=')) {
                    let params;
                    if (window.location.href.includes('?')) {
                        params = new URLSearchParams(window.location.search);
                    } else if (window.location.href.includes('#')) {
                        params = new URLSearchParams(window.location.href.split('#')[1]);
                    }
                    
                    if (params) {
                        const googleId = params.get('google_id');
                        const name = params.get('name');
                        const email = params.get('email');
                        const picture = params.get('picture');
                        
                        googleParamsInfo = `
                            <p><strong>Google ID:</strong> ${googleId || 'not found'}</p>
                            <p><strong>Name:</strong> ${name || 'not found'}</p>
                            <p><strong>Email:</strong> ${email || 'not found'}</p>
                            <p><strong>Picture:</strong> ${picture ? 'exists' : 'not found'}</p>
                        `;
                    }
                }
                
                const debugInfo = document.createElement('div');
                debugInfo.className = 'debug-info';
                debugInfo.innerHTML = `
                    <hr>
                    <h4>Debug Info</h4>
                    <p><strong>Hostname:</strong> ${window.location.hostname}</p>
                    <p><strong>Full URL:</strong> ${window.location.href}</p>
                    <p><strong>User Agent:</strong> ${navigator.userAgent}</p>
                    ${googleParamsInfo}
                    ${lastRedirectInfo}
                    <div class="debug-actions">
                        <button id="toggleDebugMode">Toggle Debug Mode</button>
                        <button id="clearDebugData">Clear Debug Data</button>
                        <button id="testLogin">Test Login</button>
                        <button id="testUrlLogin">Login from URL</button>
                    </div>
                `;
                loginMessage.parentNode.appendChild(debugInfo);
                
                // Add toggle button handler
                document.getElementById('toggleDebugMode').addEventListener('click', function() {
                    const isDebugMode = localStorage.getItem('debugMode') === 'true';
                    localStorage.setItem('debugMode', isDebugMode ? 'false' : 'true');
                    alert('Debug mode ' + (isDebugMode ? 'disabled' : 'enabled') + '. Reload the page to apply changes.');
                });
                
                // Add clear button handler
                document.getElementById('clearDebugData').addEventListener('click', function() {
                    localStorage.removeItem('lastGoogleRedirect');
                    alert('Debug data cleared. Reload the page to see changes.');
                });
                
                // Add test login button handler
                document.getElementById('testLogin').addEventListener('click', function() {
                    mockGoogleLogin(
                        'test-google-id',
                        'Test User',
                        'test@example.com',
                        'https://ui-avatars.com/api/?name=Test+User&background=random'
                    );
                });
                
                // 添加从URL登录的按钮处理
                document.getElementById('testUrlLogin').addEventListener('click', function() {
                    if (testLoginFromCurrentUrl()) {
                        alert('Successfully logged in from URL parameters');
                    } else {
                        alert('Failed to login from URL. Check console for details.');
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error showing debug info:', error);
    }
}

// Document ready event
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    // 自动处理URL中的登录参数
    const currentUrl = window.location.href;
    if (currentUrl.includes('google_id=')) {
        console.log('Detected google_id in URL, attempting direct login');
        
        // 添加应急登录按钮
        const loginSection = document.getElementById('loginSection');
        if (loginSection) {
            const emergencyBtn = document.createElement('div');
            emergencyBtn.innerHTML = `
                <div style="margin-top: 20px; text-align: center;">
                    <p>If automatic login fails, please click the button below</p>
                    <button id="emergencyLoginBtn" style="padding: 10px 15px; background-color: #5e72e4; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        Login directly from URL
                    </button>
                </div>
            `;
            loginSection.appendChild(emergencyBtn);
            
            // 添加紧急登录按钮事件
            document.getElementById('emergencyLoginBtn').addEventListener('click', function() {
                console.log('Emergency login button clicked');
                if (testLoginFromCurrentUrl()) {
                    alert('Login successful!');
                } else {
                    alert('Login failed, please check the console for more information');
                }
            });
        }
        
        // 尝试自动登录
        processGoogleLoginData();
    }
    
    // 显示调试信息
    showDebugInfo();
    
    const navLinks = document.querySelectorAll('nav ul li a');
    const sections = document.querySelectorAll('.page-section');
    const dreamInput = document.getElementById('dreamInput');
    const interpretButton = document.getElementById('interpretButton');
    const clearButton = document.getElementById('clearButton');
    const resultsSection = document.getElementById('results');
    const modelInfo = document.getElementById('modelInfo');
    const privacyLink = document.getElementById('privacyLink');
    const termsLink = document.getElementById('termsLink');
    const userAgreementLink = document.getElementById('userAgreementLink');
    const privacyModal = document.getElementById('privacyModal');
    const termsModal = document.getElementById('termsModal');
    const userAgreementModal = document.getElementById('userAgreementModal');
    // 关闭按钮
    const closeButtons = document.querySelectorAll('.modal .close');

    if (privacyLink && privacyModal) {
        privacyLink.addEventListener('click', function(e) {
            e.preventDefault();
            privacyModal.style.display = 'block';
        });
    }
    if (termsLink && termsModal) {
        termsLink.addEventListener('click', function(e) {
            e.preventDefault();
            termsModal.style.display = 'block';
        });
    }
    if (userAgreementLink && userAgreementModal) {
        userAgreementLink.addEventListener('click', function(e) {
            e.preventDefault();
            userAgreementModal.style.display = 'block';
        });
    }
    // 关闭弹窗
    closeButtons.forEach(function(btn) {
        btn.addEventListener('click', function() {
            btn.closest('.modal').style.display = 'none';
        });
    });
    // 点击modal外部关闭
    window.onclick = function(event) {
        [privacyModal, termsModal, userAgreementModal].forEach(function(modal) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    };
    
    
    const loginSection = document.getElementById('loginSection');
    const loginMessage = document.getElementById('loginMessage');
    
    // Call updateAuthUI on page load
    updateAuthUI();
    
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
    
    // Interpret button handler
    if (interpretButton) {
        interpretButton.addEventListener('click', function() {
            // Get dream text
            const dreamText = dreamInput.value.trim();
            if (!dreamText) {
                resultsSection.innerHTML = '<p style="color: red;">Please enter your dream description!</p>';
                return;
            }
            // Show loading state
            resultsSection.style.display = 'block';
            resultsSection.innerHTML = '<p class="loading">Interpreting your dream...</p>';
            // Increment usage count for non-logged in users
            incrementUsageCount();
            interpretDream(dreamText)
                .then(result => {
                    displayResults(result);
                })
                .catch(error => {
                    resultsSection.innerHTML = `
                        <div class="error-message">
                            <p>Sorry, there was an error interpreting your dream:</p>
                            <p>${error.message}</p>
                        </div>
                    `;
                });
        });
    }
    
    // Function to display interpretation results
    function displayResults(result) {
        let html = '';
        // Summary section
        html += `
            <div class="result-section">
                <h3><i class="fas fa-moon"></i> Dream Interpretation</h3>
                <div class="dream-interpretation-text">${marked.parse(result.summary)}</div>
            </div>
        `;
        // Symbols section if available
        if (result.symbols && result.symbols.length > 0) {
            html += `
                <div class="result-section">
                    <h3><i class="fas fa-star"></i> Dream Symbols</h3>
                    <div class="symbols-container">
                        ${result.symbols.map(symbol => `
                            <div class="symbol-card">
                                <h4 class="keyword">${symbol.symbol}</h4>
                                <div class="interpretation">${symbol.interpretation}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        // Psychological perspective if available
        if (result.psychological_perspective) {
            html += `
                <div class="result-section">
                    <h3><i class="fas fa-brain"></i> Psychological Perspective</h3>
                    <div class="psych-content">
                        <p>${result.psychological_perspective}</p>
                    </div>
                </div>
            `;
        }
        // Questions for reflection
        html += `
            <div class="result-section">
                <h3><i class="fas fa-question-circle"></i> Questions for Reflection</h3>
                <ul class="reflection-questions">
                    <li>What emotions did you feel during this dream?</li>
                    <li>Do any elements of the dream connect to your current life situation?</li>
                    <li>What might this dream be trying to tell you?</li>
                    <li>If you could change this dream, what would you change?</li>
                </ul>
            </div>
        `;
        resultsSection.innerHTML = html;
    }
    
    // Clear button handler
    if (clearButton) {
        clearButton.addEventListener('click', function() {
            dreamInput.value = '';
            resultsSection.style.display = 'none';
            resultsSection.innerHTML = '';
        });
    }
    
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
    const navLogin = document.getElementById('navLogin');
    if (navLogin) {
        navLogin.addEventListener('click', function(e) {
        e.preventDefault();
        if (isLoggedIn()) {
            logout();
        } else {
                handleGoogleLogin();
        }
    });
    }
    
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
});

// Fallback function for Google login in local development
function mockGoogleLogin(googleId, name, email, picture) {
    try {
        console.log('[MOCK LOGIN] Starting mock login process');
        
        // 允许在localhost和qhdsalsm.com上使用模拟登录
        const isAllowedDomain = window.location.hostname === 'localhost' || 
                               window.location.hostname === '127.0.0.1' ||
                               window.location.hostname === 'qhdsalsm.com' ||
                               window.location.hostname === 'www.qhdsalsm.com';
        
        if (!isAllowedDomain) {
            console.log('[MOCK LOGIN] Not an allowed domain:', window.location.hostname);
            return false; // Only use mock in allowed domains
        }
        
        if (!googleId) {
            console.error('[MOCK LOGIN] Google ID is required but was not provided');
            return false;
        }
        
        debugLog('Using mock Google login for development/testing');
        console.log('[MOCK LOGIN] Using mock login with data:', { 
            googleId, 
            name: name || '(not provided)', 
            email: email || '(not provided)'
        });
        
        // 创建mock用户数据
        const userData = {
            userId: 'mock-' + Date.now(),
            username: name || email || 'Local User',
            token: 'mock-token-' + Math.random().toString(36).substring(2),
            googleId: googleId,
            picture: picture || 'https://ui-avatars.com/api/?name=' + encodeURIComponent(name || 'User') + '&background=random',
            email: email || '' // 确保包含 email 字段
        };
        
        console.log('[MOCK LOGIN] Generated user data:', userData);
        
        try {
            // 直接操作localStorage，避免使用异步login函数
            console.log('[MOCK LOGIN] Storing user data directly to localStorage');
            localStorage.setItem('user', JSON.stringify(userData));
            localStorage.removeItem('usageCount');
            console.log('[MOCK LOGIN] User data stored successfully');
                
                // Update UI
                updateAuthUI();
            console.log('[MOCK LOGIN] UI updated');
            
            // Force a refresh of the dropdown functionality
            setTimeout(() => {
                initializeUserDropdown();
                console.log('[MOCK LOGIN] Dropdown functionality initialized');
            }, 100);
            
            // Show success message
            try {
                const mainElement = document.querySelector('main');
                if (mainElement) {
                    const messageElement = document.createElement('div');
                    messageElement.className = 'success-message';
                    messageElement.textContent = 'Google login successful! Welcome ' + userData.username;
                    mainElement.prepend(messageElement);
                    console.log('[MOCK LOGIN] Success message displayed');
                    
                    // Remove message after 3 seconds
                    setTimeout(() => {
                        messageElement.remove();
                    }, 3000);
                } else {
                    console.error('[MOCK LOGIN] Main element not found for displaying message');
                }
            } catch (msgError) {
                console.error('[MOCK LOGIN] Error displaying success message:', msgError);
            }
            
            // Clean URL
            try {
                const cleanUrl = window.location.origin + window.location.pathname;
                window.history.replaceState({}, document.title, cleanUrl);
                console.log('[MOCK LOGIN] URL cleaned');
            } catch (urlError) {
                console.error('[MOCK LOGIN] Error cleaning URL:', urlError);
            }
                
                // Show home section
            try {
                const navLinks = document.querySelectorAll('nav ul li a');
                navLinks.forEach(l => l.classList.remove('active'));
                
                const navHome = document.getElementById('navHome');
                if (navHome) {
                    navHome.classList.add('active');
                    console.log('[MOCK LOGIN] Navigation updated');
                }
                
                const sections = document.querySelectorAll('.page-section');
                sections.forEach(s => s.classList.remove('active'));
                
                const homeSection = document.getElementById('homeSection');
                if (homeSection) {
                    homeSection.classList.add('active');
                    console.log('[MOCK LOGIN] Home section activated');
                }
            } catch (navError) {
                console.error('[MOCK LOGIN] Error updating navigation:', navError);
            }
            
            console.log('[MOCK LOGIN] Login process completed successfully');
            return true;
        } catch (loginError) {
            console.error('[MOCK LOGIN] Critical error during login process:', loginError);
            return false;
        }
            } catch (error) {
        console.error('[MOCK LOGIN] Unhandled error in mock Google login:', error);
        return false;
    }
}

// 添加这个函数，用于直接从URL解析Google登录参数并进行模拟登录
function testLoginFromCurrentUrl() {
    try {
        debugLog('Testing login from current URL');
        const url = window.location.href;
        console.log('[EMERGENCY LOGIN] Processing URL:', url);
        
        // 如果URL中包含Google ID参数
        if (url.includes('google_id=')) {
            let params;
            let googleId, name, email, picture;
            
            // 从URL中解析参数，支持query参数或hash参数
            if (url.includes('?google_id=')) {
                params = new URLSearchParams(window.location.search);
                googleId = params.get('google_id');
                name = params.get('name');
                email = params.get('email');
                picture = params.get('picture');
                console.log('[EMERGENCY LOGIN] Using query parameters');
            } else if (url.includes('#google_id=')) {
                const hashPart = url.split('#')[1];
                params = new URLSearchParams(hashPart);
                googleId = params.get('google_id');
                name = params.get('name');
                email = params.get('email');
                picture = params.get('picture');
                console.log('[EMERGENCY LOGIN] Using hash parameters');
            } else {
                // 尝试直接从URL中提取参数
                console.log('[EMERGENCY LOGIN] Trying to extract parameters directly from URL');
                
                // 提取google_id
                const googleIdMatch = url.match(/google_id=([^&"\s<>]+)/);
                googleId = googleIdMatch ? googleIdMatch[1] : null;
                
                // 提取name
                const nameMatch = url.match(/name=([^&"\s<>]+)/);
                name = nameMatch ? decodeURIComponent(nameMatch[1]) : null;
                
                // 提取email
                const emailMatch = url.match(/email=([^&"\s<>]+)/);
                email = emailMatch ? decodeURIComponent(emailMatch[1]) : null;
                
                // 提取picture
                const pictureMatch = url.match(/picture=([^&"\s<>]+)/);
                picture = pictureMatch ? decodeURIComponent(pictureMatch[1]) : null;
            }
            
            console.log('[EMERGENCY LOGIN] Extracted parameters:', {
                googleId,
                name,
                email,
                picture: picture ? 'exists' : 'missing'
            });
            
            if (googleId) {
                // 直接使用提取的参数进行模拟登录
                console.log('[EMERGENCY LOGIN] Attempting login with extracted parameters');
                return mockGoogleLogin(googleId, name, email, picture);
            } else {
                console.log('[EMERGENCY LOGIN] Failed to extract google_id');
            }
        } else {
            console.log('[EMERGENCY LOGIN] No google_id found in URL');
        }
        
        return false;
    } catch (error) {
        console.error('[EMERGENCY LOGIN] Error:', error);
        debugLog('Error in testLoginFromCurrentUrl', error.message);
        return false;
    }
}

// 应急登录函数 - 可以在控制台中直接调用
function emergencyLogin(name, email) {
    console.log('[EMERGENCY] Executing emergency login');
    
    const googleId = 'emergency-' + Date.now();
    const username = name || email || 'Emergency User';
    const picture = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(username) + '&background=random';
    
    // 创建应急用户数据
    const userData = {
        userId: 'emergency-' + Date.now(),
        username: username,
        token: 'emergency-token-' + Math.random().toString(36).substring(2),
        googleId: googleId,
        picture: picture
    };
    
    // 存储到localStorage
    login(userData)
        .then(() => {
            console.log('[EMERGENCY] User data stored');
            // 更新UI
                updateAuthUI();
            console.log('[EMERGENCY] UI updated');
            
            // 清理URL
            try {
                const cleanUrl = window.location.origin + window.location.pathname;
                window.history.replaceState({}, document.title, cleanUrl);
                console.log('[EMERGENCY] URL cleaned');
            } catch (e) {
                console.error('[EMERGENCY] Error cleaning URL:', e);
            }
            
            console.log('[EMERGENCY] Emergency login completed');
            alert('Emergency login successful!');
        })
        .catch(error => {
            console.error('[EMERGENCY] Error during login:', error);
            alert('Emergency login failed: ' + error.message);
        });
    
    return 'Emergency login program started, please check the console for detailed information';
}

// 暴露到全局范围以便从控制台调用
window.emergencyLogin = emergencyLogin; 

// 通义千问plus模型解梦API
async function interpretDream(dreamText) {
    const endpoint = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions';
    const apiKey = 'sk-c78ff1c1f9dc469992497b2b678f8657';
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
    };
    const body = {
        model: 'qwen-plus',
        messages: [
            { role: 'system', content: '你是专业的梦境解读师，请根据用户输入的梦境内容，结合心理学、文化象征等多角度，给出详细、启发性且温和的解梦分析。' },
            { role: 'user', content: dreamText }
        ]
    };
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers,
            body: JSON.stringify(body)
        });
        if (!response.ok) {
            throw new Error('API请求失败: ' + response.status);
        }
        const data = await response.json();
        // 兼容OpenAI格式
        const reply = data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content
            ? data.choices[0].message.content
            : '未能获取有效的解梦结果。';
        return {
            summary: reply,
            symbols: [],
            psychological_perspective: '',
            is_offline: false
        };
    } catch (error) {
        return {
            summary: '解梦服务出错: ' + error.message,
            symbols: [],
            psychological_perspective: '',
            is_offline: false
        };
    }
}

// 段落格式化函数
function formatParagraphs(text) {
    return text
        .split(/\n{2,}/)
        .map(paragraph => `<p>${paragraph.replace(/\n/g, '<br>')}</p>`)
        .join('');
} 