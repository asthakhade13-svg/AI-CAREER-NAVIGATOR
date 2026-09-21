// ============================================
// API.JS — Central API Configuration
// All API calls go through this file
// ============================================

// Spring Boot backend URL (defaults to localhost:8080 or custom configured URL)
const API_BASE_URL = localStorage.getItem('SPRING_API_BASE_URL') || 'http://localhost:8080/api/v1';






// ============================================
// TOKEN MANAGEMENT
// Save and get JWT token from localStorage
// ============================================
 const TokenManager = {

    save: (token) => {
        localStorage.setItem('jwt_token', token);
    },

    get: () => {
        return localStorage.getItem('jwt_token');
    },

    // Clear ALL stored data on logout
    remove: () => {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user_data');
        localStorage.clear(); // Clear everything!
    },

    exists: () => {
        return !!localStorage.getItem('jwt_token');
    }
};

// ============================================
// USER DATA MANAGEMENT
// ============================================
const UserManager = {

    save: (userData) => {
        localStorage.setItem(
            'user_data',
            JSON.stringify(userData)
        );
    },

    get: () => {
        const data = localStorage
            .getItem('user_data');
        return data ? JSON.parse(data) : null;
    }
};

// ============================================
// API CALL HELPER
// Makes HTTP requests with JWT token
// ============================================
 async function apiCall(endpoint, method = 'GET',
                       body = null) {
    const url = API_BASE_URL + endpoint;

    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };

    // Add JWT token if exists
    const token = TokenManager.get();
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }

    const options = {
        method: method,
        headers: headers,
        mode: 'cors'  // ← ADD THIS LINE!
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        const data = await response.json();
        return { status: response.status, data: data };
    } catch (error) {
        console.error('API Error:', error);
        return {
            status: 500,
            data: {
                message: 'Connection error! ' +
                         'Is backend running?'
            }
        };
    }
}

// ============================================
// AUTH APIs
// ============================================
const AuthAPI = {

    register: (userData) =>
        apiCall('/auth/register', 'POST', userData),

    login: (credentials) =>
        apiCall('/auth/login', 'POST', credentials),

    logout: () => {
        TokenManager.remove();
        window.location.href = 'index.html';
    }
};

// ============================================
// QUIZ APIs
// ============================================
const QuizAPI = {

    getQuestions: () =>
        apiCall('/quiz/questions', 'GET'),

    submitQuiz: (answers) =>
        apiCall('/quiz/submit', 'POST', { answers }),

    getHistory: () =>
        apiCall('/quiz/history', 'GET')
};

// ============================================
// CAREER APIs
// ============================================
const CareerAPI = {

    generateRecommendations: () =>
        apiCall('/career/recommend', 'POST'),

    getRecommendations: () =>
        apiCall('/career/my-recommendations', 'GET')
};

// ============================================
// ROADMAP APIs
// ============================================
const RoadmapAPI = {

    generate: () =>
        apiCall('/roadmap/generate', 'POST'),

    getMyRoadmap: () =>
        apiCall('/roadmap/my-roadmap', 'GET'),

    completeMilestone: (milestoneId) =>
        apiCall(
            '/roadmap/complete/' + milestoneId,
            'PUT'
        )
};

// ============================================
// CHAT APIs
// ============================================
const ChatAPI = {

    sendMessage: (message, chatType = 'GENERAL') =>
        apiCall('/chat/message', 'POST', {
            message,
            chatType
        }),

    getHistory: () =>
        apiCall('/chat/history', 'GET')
};

// ============================================
// PROGRESS APIs
// ============================================
const ProgressAPI = {

    getDashboard: () =>
        apiCall('/progress/dashboard', 'GET'),

    getStats: () =>
        apiCall('/progress/stats', 'GET')
};

// ============================================
// PROTECT PAGES
// Call this on every protected page
// ============================================
function requireAuth() {
    if (!TokenManager.exists()) {
        window.location.href = '../index.html';
        return false;
    }
    return true;
}

// ============================================
// SHOW LOADING SPINNER
// ============================================
function showLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML =
            '<div style="text-align:center;' +
            'padding:20px">' +
            '<i class="fas fa-spinner fa-spin" ' +
            'style="font-size:2rem;' +
            'color:var(--primary)"></i>' +
            '<p>Loading...</p></div>';
    }
}

// ============================================
// SHOW ERROR MESSAGE
// ============================================
function showError(message) {
    const toast = document.createElement('div');
    toast.style.cssText =
        'position:fixed;top:20px;right:20px;' +
        'background:#EF4444;color:white;' +
        'padding:14px 20px;border-radius:10px;' +
        'z-index:9999;font-weight:600;' +
        'box-shadow:0 4px 12px rgba(0,0,0,0.2)';
    toast.textContent = '❌ ' + message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// ============================================
// SHOW SUCCESS MESSAGE
// ============================================
function showSuccess(message) {
    const toast = document.createElement('div');
    toast.style.cssText =
        'position:fixed;top:20px;right:20px;' +
        'background:#10B981;color:white;' +
        'padding:14px 20px;border-radius:10px;' +
        'z-index:9999;font-weight:600;' +
        'box-shadow:0 4px 12px rgba(0,0,0,0.2)';
    toast.textContent = '✅ ' + message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}


// ============================================
// UPDATE SIDEBAR WITH CURRENT USER
// This runs on EVERY page automatically
// ============================================
function updateSidebarUser() {

    // Get logged in user from localStorage
    const user = UserManager.get();

    // If no user found — stop
    if (!user) return;

    // ---- Update ALL name elements ----
    // Finds every element with class "user-info"
    // and updates the <strong> tag inside it
    document.querySelectorAll('.user-info strong')
        .forEach(function(el) {
            el.textContent = user.fullName;
        });

    // ---- Update ALL avatar circles ----
    // Changes "R" to first letter of user name
    document.querySelectorAll('.user-avatar')
        .forEach(function(el) {
            // Only change if it's a single letter
            if (el.textContent.trim().length <= 2) {
                el.textContent =
                    user.fullName
                        .charAt(0)
                        .toUpperCase();
            }
        });

    // ---- Update welcome message ----
    // Changes "Welcome back, Rahul!"
    // to "Welcome back, dev!"
    const welcomeEl =
        document.querySelector('.topbar-sub');
    if (welcomeEl) {
        const firstName =
            user.fullName.split(' ')[0];
        welcomeEl.textContent =
            'Welcome back, ' + firstName + '! 👋';
    }
}

// ---- Logout Function ----
function logout() {
    // Clear ALL saved data
    localStorage.clear();

    // Check which folder we are in
    const path = window.location.pathname;
    if (path.includes('/pages/')) {
        // We are inside pages/ folder
        window.location.href = '../index.html';
    } else {
        // We are in root folder
        window.location.href = 'index.html';
    }
}

// ---- Auto run when page loads ----
// This makes it work on EVERY page
// without needing to call it manually
document.addEventListener(
    'DOMContentLoaded',
    updateSidebarUser
);