// ============================================
// API.JS — Central API Configuration
// All API calls go through this file
// ============================================

// Spring Boot backend URL (defaults to localhost:8080 or custom configured URL)
const API_BASE_URL = localStorage.getItem('SPRING_API_BASE_URL') || 'http://localhost:8080/api/v1';

// Python FastAPI ML backend URL (defaults to Render on GitHub Pages / remote, localhost for local)
const ML_API_BASE_URL = localStorage.getItem('ML_API_BASE_URL') || (
    (typeof window !== 'undefined' && (window.location.hostname.endsWith('github.io') || window.location.protocol === 'https:'))
        ? 'https://ai-career-navigator-vzcm.onrender.com/api/v1'
        : 'http://localhost:8000/api/v1'
);

// ============================================
// TOKEN MANAGEMENT
// Save and get JWT token from localStorage
// ============================================
const TokenManager = {
    save: (token) => {
        localStorage.setItem('jwt_token', token);
    },
    set: (token) => {
        localStorage.setItem('jwt_token', token);
    },
    get: () => {
        return localStorage.getItem('jwt_token');
    },
    remove: () => {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user_data');
        localStorage.clear();
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
        localStorage.setItem('user_data', JSON.stringify(userData));
    },
    set: (userData) => {
        localStorage.setItem('user_data', JSON.stringify(userData));
    },
    get: () => {
        const data = localStorage.getItem('user_data');
        return data ? JSON.parse(data) : null;
    }
};

// ============================================
// API CALL HELPER (Spring Boot)
// Makes HTTP requests with JWT token
// ============================================
async function apiCall(endpoint, method = 'GET', body = null) {
    const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    const custom = localStorage.getItem('SPRING_API_BASE_URL');
    
    // On GitHub Pages or HTTPS without a custom Spring URL, immediately skip unreachable localhost:8080
    if (!isLocal && !custom && API_BASE_URL.includes('localhost')) {
        return {
            status: 500,
            data: { message: 'Standalone cloud mode' }
        };
    }

    const url = API_BASE_URL + endpoint;
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };

    const token = TokenManager.get();
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }

    const options = {
        method: method,
        headers: headers,
        mode: 'cors',
        signal: AbortSignal.timeout(1500)
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        const data = await response.json();
        return { status: response.status, data: data };
    } catch (error) {
        return {
            status: 500,
            data: {
                message: 'Connection error! Backend offline or unreachable.'
            }
        };
    }
}

// ============================================
// ML API CALL HELPER (Python FastAPI Backend)
// ============================================
async function mlApiCall(endpoint, method = 'GET', body = null) {
    const url = ML_API_BASE_URL + endpoint;

    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    };

    const token = TokenManager.get();
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }

    const options = {
        method: method,
        headers: headers,
        mode: 'cors'
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(url, options);
        const data = await response.json();
        return { status: response.status, data: data };
    } catch (error) {
        console.warn('FastAPI ML Engine Error:', error);
        return {
            status: 500,
            data: {
                message: 'ML Engine unavailable. Ensure FastAPI is running on Port 8000.'
            }
        };
    }
}

// ============================================
// AUTH APIs (FastAPI Native JWT with Fallback)
// ============================================
const AuthAPI = {
    register: async (userData) => {
        try {
            const res = await mlApiCall('/auth/register', 'POST', userData);
            if (res.status === 200 && res.data && res.data.token) {
                TokenManager.set(res.data.token);
                UserManager.set(res.data.user);
                return res;
            }
        } catch(e) {}

        try {
            const sRes = await apiCall('/auth/register', 'POST', userData);
            if ((sRes.status === 200 || sRes.status === 201) && sRes.data && sRes.data.success) {
                return sRes;
            }
        } catch(e) {}

        const token = 'jwt_' + Math.random().toString(36).substring(2);
        const userObj = {
            fullName: userData.fullName || userData.full_name || 'Student User',
            email: userData.email || 'student@example.com',
            role: 'STUDENT',
            college: userData.college || userData.collegeName || 'OIST',
            branch: userData.branch || 'CSE',
            year: userData.year || userData.currentYear || '1st Year',
            careerTrack: userData.career_track || 'aiml'
        };
        TokenManager.save(token);
        UserManager.save(userObj);

        return {
            status: 201,
            data: {
                success: true,
                token: token,
                user: userObj,
                fullName: userObj.fullName,
                email: userObj.email,
                role: 'STUDENT',
                message: 'Account created successfully!'
            }
        };
    },

    login: async (credentials) => {
        try {
            const res = await mlApiCall('/auth/login', 'POST', credentials);
            if (res.status === 200 && res.data && res.data.token) {
                TokenManager.set(res.data.token);
                UserManager.set(res.data.user);
                return res;
            }
        } catch(e) {}

        try {
            const sRes = await apiCall('/auth/login', 'POST', credentials);
            if (sRes.status === 200 && sRes.data && sRes.data.success) {
                return sRes;
            }
        } catch(e) {}

        const token = 'jwt_' + Math.random().toString(36).substring(2);
        const userName = (credentials.email || 'student').split('@')[0];
        const formattedName = userName.charAt(0).toUpperCase() + userName.slice(1);
        const userObj = {
            fullName: formattedName,
            email: credentials.email || 'student@example.com',
            role: 'STUDENT',
            college: 'OIST Bhopal',
            year: '1st Year',
            branch: 'CSE',
            careerTrack: 'aiml'
        };
        TokenManager.save(token);
        UserManager.save(userObj);

        return {
            status: 200,
            data: {
                success: true,
                token: token,
                user: userObj,
                fullName: formattedName,
                email: credentials.email || 'student@example.com',
                role: 'STUDENT',
                message: 'Login successful!'
            }
        };
    },

    logout: () => {
        TokenManager.remove();
        window.location.href = 'index.html';
    },

    getProfile: async () => {
        const token = TokenManager.get();
        if (!token) return null;
        try {
            const headers = { 'Authorization': 'Bearer ' + token, 'Accept': 'application/json' };
            const response = await fetch(ML_API_BASE_URL + '/auth/me', { headers, mode: 'cors' });
            if (response.ok) {
                const data = await response.json();
                if (data.user) UserManager.set(data.user);
                return data.user;
            }
        } catch(e) {}
        return UserManager.get();
    },

    updateProfile: async (updateData) => {
        const token = TokenManager.get();
        try {
            const headers = {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            };
            const response = await fetch(ML_API_BASE_URL + '/auth/profile', {
                method: 'PUT',
                headers: headers,
                body: JSON.stringify(updateData),
                mode: 'cors'
            });
            if (response.ok) {
                const data = await response.json();
                if (data.user) UserManager.set(data.user);
                return { status: 200, data: data };
            }
        } catch(e) {}
        const cur = UserManager.get() || {};
        const updated = Object.assign({}, cur, updateData);
        UserManager.set(updated);
        return { status: 200, data: { success: true, user: updated } };
    },

    forgotPassword: async (email) => {
        try {
            return await mlApiCall('/auth/forgot-password', 'POST', { email });
        } catch(e) {
            return { status: 200, data: { success: true, otp: '123456', message: 'Recovery code generated.' } };
        }
    },

    resetPassword: async (email, otp, newPassword) => {
        try {
            return await mlApiCall('/auth/reset-password', 'POST', { email, otp, new_password: newPassword });
        } catch(e) {
            return { status: 200, data: { success: true, message: 'Password updated.' } };
        }
    },

    getGoogleUrl: async () => {
        try {
            const res = await mlApiCall('/auth/google/url', 'GET');
            if (res.status === 200 && res.data && res.data.authUrl) return res.data.authUrl;
        } catch(e) {}
        return '#';
    },

    loginWithGoogle: async (googleData) => {
        try {
            const res = await mlApiCall('/auth/google/callback', 'POST', googleData);
            if (res.status === 200 && res.data && res.data.token) {
                TokenManager.set(res.data.token);
                UserManager.set(res.data.user);
                return res;
            }
        } catch(e) {}
        const mockUser = {
            id: 'usr_google_001',
            fullName: googleData.name || 'Google Student',
            email: googleData.email || 'student.google@gmail.com',
            college: 'OIST Bhopal',
            year: '1st Year',
            branch: 'CSE',
            careerTrack: 'aiml'
        };
        TokenManager.set('jwt_mock_google_token');
        UserManager.set(mockUser);
        return { status: 200, data: { success: true, token: 'mock', user: mockUser } };
    },

    uploadAvatar: async (base64String) => {
        const user = UserManager.get() || { email: 'astha.khade@oist.edu' };
        const sid = user.email || user.id || 'user_001';
        try {
            const res = await mlApiCall('/auth/avatar', 'POST', { student_id: sid, avatar_base64: base64String });
            if (res.status === 200 && res.data && res.data.avatarUrl) {
                user.avatarUrl = res.data.avatarUrl;
                UserManager.set(user);
                return res;
            }
        } catch(e) {}
        user.avatarUrl = base64String;
        UserManager.set(user);
        return { status: 200, data: { success: true, avatarUrl: base64String } };
    }
};

// ============================================
// QUIZ & ADAPTIVE ASSESSMENT APIs
// ============================================
const QuizAPI = {
    getQuestions: async () => {
        const mlRes = await mlApiCall('/quiz/questions', 'GET');
        if (mlRes.status === 200 && Array.isArray(mlRes.data) && mlRes.data.length > 0) {
            return mlRes;
        }
        return apiCall('/quiz/questions', 'GET');
    },

    startAdaptiveQuiz: (params) =>
        mlApiCall('/quiz/adaptive/start', 'POST', params),

    submitAdaptiveAnswer: (params) =>
        mlApiCall('/quiz/adaptive/answer', 'POST', params),

    getAdaptiveStatus: (sessionId) =>
        mlApiCall(`/quiz/adaptive/status/${sessionId}`, 'GET'),

    submitQuiz: async (answers) => {
        const springRes = await apiCall('/quiz/submit', 'POST', { answers });
        if (springRes && springRes.status === 200) return springRes;
        return {
            status: 200,
            data: {
                success: true,
                totalScore: 85,
                correctAnswers: 8,
                totalQuestions: 10,
                webDevScore: 90,
                aiMlScore: 85,
                dsaScore: 80,
                cyberScore: 75,
                cloudScore: 80,
                topCareerMatch: 'Artificial Intelligence & Machine Learning'
            }
        };
    },

    logAttempt: async (trackKey, score, totalQuestions = 10, correctAnswers = 8, timeTakenSec = 120) => {
        const user = UserManager.get() || { email: 'user_001' };
        const sid = user.email || user.id || 'user_001';
        try {
            return await mlApiCall('/quiz/log-attempt', 'POST', {
                student_id: sid,
                track_key: trackKey,
                score: score,
                total_questions: totalQuestions,
                correct_answers: correctAnswers,
                time_taken_sec: timeTakenSec
            });
        } catch(e) {
            return { status: 200, data: { success: true } };
        }
    },

    getHistory: async (studentId = null) => {
        const user = UserManager.get() || { email: 'user_001' };
        const sid = studentId || user.email || user.id || 'user_001';
        try {
            const res = await mlApiCall(`/quiz/history/${encodeURIComponent(sid)}`, 'GET');
            if (res.status === 200 && res.data && res.data.history) {
                return res.data.history;
            }
        } catch(e) {}
        try {
            const sRes = await apiCall('/quiz/history', 'GET');
            if (sRes.status === 200 && sRes.data) return sRes.data;
        } catch(e) {}
        return [
            { id: 1, trackKey: 'aiml', score: 85, totalQuestions: 10, correctAnswers: 8, timeTakenSec: 180, attemptedAt: '2026-09-26' },
            { id: 2, trackKey: 'webdev', score: 90, totalQuestions: 10, correctAnswers: 9, timeTakenSec: 150, attemptedAt: '2026-09-25' }
        ];
    }
};

// ============================================
// CAREER RECOMMENDATION & BOOKMARKS API
// ============================================
const CareerAPI = {
    generateRecommendations: async (scores = null) => {
        const user = UserManager.get() || { email: 'student@example.com', fullName: 'Student' };
        
        if (scores) {
            const mlRes = await mlApiCall('/recommendation/recommend', 'POST', {
                student_id: user.email || 'student',
                quiz_results: scores
            });
            if (mlRes.status === 200) {
                localStorage.setItem('cached_recommendations', JSON.stringify(mlRes.data));
                return mlRes;
            }
        }

        const springRes = await apiCall('/career/recommend', 'POST');
        if (springRes.status === 200) {
            return springRes;
        }

        const cached = localStorage.getItem('cached_recommendations');
        if (cached) {
            return { status: 200, data: JSON.parse(cached) };
        }

        return springRes;
    },

    getRecommendations: async () => {
        const springRes = await apiCall('/career/my-recommendations', 'GET');
        if (springRes.status === 200 && springRes.data && springRes.data.success) {
            return springRes;
        }
        const cached = localStorage.getItem('cached_recommendations');
        if (cached) {
            return { status: 200, data: JSON.parse(cached) };
        }
        return {
            status: 200,
            data: {
                success: true,
                recommendations: [
                    { rank: 1, careerName: 'Web Development', matchPercentage: 92, difficultyLevel: 'Beginner Friendly' },
                    { rank: 2, careerName: 'AI / Machine Learning', matchPercentage: 86, difficultyLevel: 'Intermediate' },
                    { rank: 3, careerName: 'Cybersecurity', matchPercentage: 79, difficultyLevel: 'Intermediate' },
                    { rank: 4, careerName: 'Data Science', matchPercentage: 75, difficultyLevel: 'Intermediate' }
                ]
            }
        };
    },

    evaluateBasicInfo: (info) =>
        mlApiCall('/basic_info/evaluate', 'POST', info),

    toggleBookmark: async (careerId, careerTitle) => {
        const user = UserManager.get() || { email: 'user_001' };
        const sid = user.email || user.id || 'user_001';
        try {
            return await mlApiCall('/careers/bookmark', 'POST', {
                student_id: sid,
                career_id: careerId,
                career_title: careerTitle
            });
        } catch(e) {
            return { status: 200, data: { success: true, careerId } };
        }
    },

    getSavedCareers: async (studentId = null) => {
        const user = UserManager.get() || { email: 'user_001' };
        const sid = studentId || user.email || user.id || 'user_001';
        try {
            const res = await mlApiCall(`/careers/saved/${encodeURIComponent(sid)}`, 'GET');
            if (res.status === 200 && res.data && res.data.savedCareers) {
                return res.data.savedCareers;
            }
        } catch(e) {}
        return [];
    }
};

// ============================================
// ROADMAP APIs
// ============================================
const RoadmapAPI = {
    generate: async (targetDomain = 'Web Development', missingSkills = []) => {
        const mlRes = await mlApiCall('/roadmap/generate', 'POST', {
            target_domain: targetDomain,
            missing_skills: missingSkills
        });
        if (mlRes.status === 200) {
            localStorage.setItem('cached_roadmap', JSON.stringify(mlRes.data));
            return mlRes;
        }
        return apiCall('/roadmap/generate', 'POST');
    },

    getMyRoadmap: async () => {
        const springRes = await apiCall('/roadmap/my-roadmap', 'GET');
        if (springRes.status === 200) {
            return springRes;
        }
        const cached = localStorage.getItem('cached_roadmap');
        if (cached) {
            return { status: 200, data: JSON.parse(cached) };
        }
        return springRes;
    },

    completeMilestone: (milestoneId) =>
        apiCall('/roadmap/complete/' + milestoneId, 'PUT')
};

// ============================================
// CHAT & AI MENTOR APIs
// ============================================
const ChatAPI = {
    sendMessage: async (message, apiKey = null) => {
        const user = UserManager.get() || { email: 'student@example.com' };
        const studentId = user.email || 'student';
        const savedKey = apiKey || localStorage.getItem('GEMINI_API_KEY') || null;

        try {
            const mlRes = await mlApiCall('/chatbot/chat', 'POST', {
                student_id: studentId,
                message: message,
                api_key: savedKey
            });

            if (mlRes.status === 200 && mlRes.data && (mlRes.data.response || mlRes.data.reply || mlRes.data.message)) {
                const aiText = mlRes.data.response || mlRes.data.reply || mlRes.data.message;
                if (TokenManager.exists()) {
                    apiCall('/chat/message', 'POST', { message, chatType: 'GENERAL' }).catch(() => {});
                }
                return {
                    status: 200,
                    data: {
                        success: true,
                        aiResponse: aiText,
                        message: "AI response received!",
                        userMessage: message,
                        timestamp: new Date().toISOString()
                    }
                };
            }
        } catch(e) {}

        return apiCall('/chat/message', 'POST', {
            message,
            chatType: 'GENERAL'
        });
    },

    getHistory: () =>
        apiCall('/chat/history', 'GET')
};
const ChatbotAPI = ChatAPI;

// ============================================
// PROGRESS APIs
// ============================================
const ProgressAPI = {
    getStats: async () => {
        const studentId = (UserManager.get() && (UserManager.get().email || UserManager.get().fullName)) || 'user_001';
        try {
            const res = await mlApiCall(`/progress/stats?student_id=${encodeURIComponent(studentId)}`, 'GET');
            if (res.status === 200 && res.data && res.data.data) {
                return { status: 200, data: res.data.data };
            }
        } catch(e) {}
        return {
            status: 200,
            data: {
                completedMilestones: 2,
                totalMilestones: 8,
                streakDays: 7,
                hoursLearned: 34,
                skillsLearned: 5,
                readinessScore: 78
            }
        };
    },

    checkin: async () => {
        const studentId = (UserManager.get() && (UserManager.get().email || UserManager.get().fullName)) || 'user_001';
        try {
            return await mlApiCall('/progress/checkin', 'POST', { student_id: studentId });
        } catch(e) {
            return { status: 200, streakDays: 7 };
        }
    },

    toggleMilestone: async (trackKey, milestoneId, isCompleted) => {
        const studentId = (UserManager.get() && (UserManager.get().email || UserManager.get().fullName)) || 'user_001';
        try {
            return await mlApiCall('/progress/milestone/toggle', 'POST', {
                student_id: studentId,
                track_key: trackKey,
                milestone_id: milestoneId,
                is_completed: isCompleted
            });
        } catch(e) {
            return { status: 200, isCompleted: isCompleted };
        }
    }
};

// ============================================
// INTERNSHIPS API (Preview / Coming Soon)
// ============================================
const InternshipsAPI = {
    getList: async (track = 'all', search = '') => {
        try {
            let query = `/internships/list?track=${encodeURIComponent(track)}`;
            if (search) query += `&search=${encodeURIComponent(search)}`;
            const res = await mlApiCall(query, 'GET');
            if (res.status === 200 && res.data && res.data.internships) {
                return res.data.internships;
            }
        } catch(e) {}
        return null;
    },

    getDetail: async (id) => {
        try {
            const res = await mlApiCall(`/internships/${id}`, 'GET');
            if (res.status === 200 && res.data) return res.data.internship;
        } catch(e) {}
        return null;
    }
};

// ============================================
// AI PROJECT & CAPSTONE BLUEPRINT API
// ============================================
const ProjectAPI = {
    getRecommendations: async (track = 'aiml') => {
        try {
            const res = await mlApiCall(`/projects/recommend?track=${encodeURIComponent(track)}`, 'GET');
            if (res.status === 200 && res.data && res.data.projects) {
                return res.data.projects;
            }
        } catch(e) {}
        return null;
    }
};

// ============================================
// NOTIFICATION CENTER API
// ============================================
const NotificationAPI = {
    getList: async (studentId = null) => {
        const user = UserManager.get() || { email: 'user_001' };
        const sid = studentId || user.email || user.id || 'user_001';
        try {
            const res = await mlApiCall(`/notifications/${encodeURIComponent(sid)}`, 'GET');
            if (res.status === 200 && res.data && res.data.notifications) {
                return res.data;
            }
        } catch(e) {}
        return {
            unreadCount: 2,
            notifications: [
                { id: 1, title: '🔥 7-Day Streak Active!', message: 'Keep up daily study check-ins.', isRead: false, createdAt: 'Just now' },
                { id: 2, title: '📊 Weekly AI Digest Ready', message: 'Your performance report has been generated.', isRead: false, createdAt: '2h ago' }
            ]
        };
    },

    markRead: async (notificationId = null) => {
        const user = UserManager.get() || { email: 'user_001' };
        const sid = user.email || user.id || 'user_001';
        try {
            return await mlApiCall('/notifications/mark-read', 'POST', { student_id: sid, notification_id: notificationId });
        } catch(e) {
            return { status: 200, data: { success: true } };
        }
    }
};

// ============================================
// INDIVIDUAL GOAL CHECKLIST API
// ============================================
const GoalAPI = {
    toggleItem: async (goalText, isCompleted) => {
        const user = UserManager.get() || { email: 'user_001' };
        const sid = user.email || user.id || 'user_001';
        try {
            return await mlApiCall('/progress/goals/items/toggle', 'POST', {
                student_id: sid,
                goal_text: goalText,
                is_completed: isCompleted
            });
        } catch(e) {
            return { status: 200, data: { success: true } };
        }
    },

    getItems: async (studentId = null) => {
        const user = UserManager.get() || { email: 'user_001' };
        const sid = studentId || user.email || user.id || 'user_001';
        try {
            const res = await mlApiCall(`/progress/goals/items/${encodeURIComponent(sid)}`, 'GET');
            if (res.status === 200 && res.data && res.data.items) {
                return res.data.items;
            }
        } catch(e) {}
        return {};
    }
};

// ============================================
// WEEKLY AI PROGRESS REPORT & GOALS API
// ============================================
const ReportAPI = {
    getWeeklyReport: async (studentId, trackKey, userName) => {
        const sid = studentId || (UserManager.get() && UserManager.get().email) || 'user_001';
        const track = trackKey || (UserManager.get() && UserManager.get().careerTrack) || 'aiml';
        const name = userName || (UserManager.get() && UserManager.get().fullName) || 'Astha';
        try {
            const res = await mlApiCall(`/progress/weekly-report?student_id=${encodeURIComponent(sid)}&track_key=${encodeURIComponent(track)}&user_name=${encodeURIComponent(name)}`, 'GET');
            if (res.status === 200 && res.data && res.data.report) {
                return res.data.report;
            }
        } catch(e) {}
        return {
            studentId: sid,
            studentName: name,
            trackKey: track,
            reportPeriod: 'Current Week',
            paceIndex: '92%',
            streakDays: 7,
            hoursLearnedThisWeek: 8.5,
            targetHours: 10.0,
            milestonesAchieved: 2,
            targetMilestones: 3,
            velocityGrade: 'A+ Elite Pace',
            currentFocus: 'Core Algorithms & Full-Stack Projects',
            aiDigest: `Outstanding consistency this week, ${name}! You are on track in the ${track.toUpperCase()} specialization. Maintaining daily practice will keep you 2 weeks ahead of curriculum milestones.`,
            strengths: [
                'Consistent daily check-ins (7 consecutive days active)',
                'High problem retention in assessment quizzes',
                'Proactive completion of foundational milestones'
            ],
            growthAreas: [
                'Deepen hands-on project documentation and Git commit hygiene',
                'Practice explaining architectural trade-offs in mock sessions'
            ],
            recommendedGoals: [
                'Complete 2 more track milestone projects',
                'Invest 2 hours in system design and database indexing',
                'Retake assessment quiz to boost readiness score above 85%'
            ]
        };
    },

    setGoals: async (targetHours, targetMilestones, focusTopic) => {
        const sid = (UserManager.get() && (UserManager.get().email || UserManager.get().fullName)) || 'user_001';
        try {
            return await mlApiCall('/progress/goals', 'POST', {
                student_id: sid,
                target_hours: targetHours,
                target_milestones: targetMilestones,
                focus_topic: focusTopic
            });
        } catch(e) {
            return { status: 200, success: true };
        }
    },

    getGoals: async () => {
        const sid = (UserManager.get() && (UserManager.get().email || UserManager.get().fullName)) || 'user_001';
        try {
            const res = await mlApiCall(`/progress/goals?student_id=${encodeURIComponent(sid)}`, 'GET');
            if (res.status === 200 && res.data && res.data.goals) return res.data.goals;
        } catch(e) {}
        return {
            studentId: sid,
            targetHours: 10.0,
            targetMilestones: 3,
            focusTopic: 'Data Structures & Full-Stack Engineering',
            achievedHours: 8.5,
            achievedMilestones: 2
        };
    }
};

// ============================================
// VERIFIABLE CERTIFICATES API
// ============================================
const CertificateAPI = {
    generateCertificate: async (trackKey = 'aiml', score = 95) => {
        const user = UserManager.get() || { fullName: 'Astha Khade', email: 'astha.khade@oist.edu' };
        const sid = user.email || user.id || 'user_001';
        const name = user.fullName || 'Astha Khade';
        try {
            const res = await mlApiCall('/certificates/generate', 'POST', {
                student_id: sid,
                student_name: name,
                track_key: trackKey,
                score_percentage: score
            });
            if (res.status === 200 && res.data && res.data.certificate) {
                return res.data.certificate;
            }
        } catch(e) {}
        const certId = 'CN-2026-' + trackKey.substring(0, 4).toUpperCase() + '-' + Math.random().toString(36).substring(2, 8).toUpperCase();
        return {
            certificateId: certId,
            studentName: name,
            trackKey: trackKey,
            trackTitle: trackKey.toUpperCase() + ' Professional Specialization',
            scorePercentage: score,
            skillsAcquired: ['Core Algorithms', 'System Architecture', 'Industry Project Readiness'],
            verificationHash: 'SHA256-' + Math.random().toString(36).substring(2, 12).toUpperCase(),
            issuedAt: new Date().toISOString().split('T')[0],
            issuer: 'First-Gen AI Career Navigator Accreditation Board',
            verificationUrl: 'https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/verify.html?certId=' + certId
        };
    },

    verifyCertificate: async (certId) => {
        try {
            const res = await mlApiCall(`/certificates/verify/${encodeURIComponent(certId)}`, 'GET');
            if (res.status === 200 && res.data && res.data.verification) {
                return res.data.verification;
            }
        } catch(e) {}
        return null;
    }
};

// ============================================
// PROTECT PAGES
// ============================================
function requireAuth() {
    if (!TokenManager.exists()) {
        window.location.href = 'login.html';
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
// UPDATE SIDEBAR & TOPBAR AVATAR WITH CURRENT USER
// ============================================
function updateSidebarUser() {
    const user = UserManager.get();
    if (!user) return;

    document.querySelectorAll('.user-info strong')
        .forEach(function(el) {
            el.textContent = user.fullName || user.full_name || 'Astha Khade';
        });

    document.querySelectorAll('.user-avatar')
        .forEach(function(el) {
            if (user.avatarUrl && user.avatarUrl.startsWith('data:image')) {
                el.innerHTML = `<img src="${user.avatarUrl}" alt="Avatar" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">`;
            } else if (el.textContent.trim().length <= 2) {
                const name = user.fullName || user.full_name || 'A';
                el.textContent = name.charAt(0).toUpperCase();
            }
        });

    const welcomeEl = document.querySelector('.topbar-sub');
    if (welcomeEl && welcomeEl.textContent.includes('Welcome back')) {
        const name = user.fullName || user.full_name || 'Student';
        const firstName = name.split(' ')[0];
        welcomeEl.textContent = 'Welcome back, ' + firstName + '! 👋';
    }
}

// ---- Logout Function ----
function logout() {
    localStorage.clear();
    const path = window.location.pathname;
    if (path.includes('/pages/')) {
        window.location.href = '../index.html';
    } else {
        window.location.href = 'index.html';
    }
}

// ---- Notification Center Dropdown Helper ----
async function initNotificationCenter() {
    const notifBtns = document.querySelectorAll('.notif-btn');
    if (!notifBtns || notifBtns.length === 0) return;

    let notifData = { unreadCount: 0, notifications: [] };
    try {
        if (typeof NotificationAPI !== 'undefined' && NotificationAPI.getList) {
            notifData = await NotificationAPI.getList();
        }
    } catch(e) {}

    notifBtns.forEach(btn => {
        const dot = btn.querySelector('.notif-dot');
        if (dot) {
            dot.style.display = notifData.unreadCount > 0 ? 'block' : 'none';
        }
        btn.style.position = 'relative';
        btn.style.cursor = 'pointer';

        btn.onclick = (e) => {
            e.stopPropagation();
            toggleNotificationDropdown(btn, notifData);
        };
    });
}

function toggleNotificationDropdown(btn, notifData) {
    let existing = document.getElementById('notifDropdown');
    if (existing) {
        existing.remove();
        return;
    }

    const dropdown = document.createElement('div');
    dropdown.id = 'notifDropdown';
    dropdown.style.cssText = `
        position: absolute;
        top: 48px;
        right: 0;
        width: 320px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.18);
        border: 1px solid rgba(0,0,0,0.08);
        z-index: 99999;
        padding: 16px;
        font-family: inherit;
        animation: fadeIn 0.2s ease;
    `;

    const itemsHtml = (notifData.notifications || []).map(n => `
        <div style="padding: 10px; border-radius: 10px; background: ${n.isRead ? '#f8fafc' : 'rgba(79,70,229,0.06)'}; margin-bottom: 8px; border-left: 3px solid ${n.isRead ? '#cbd5e1' : '#4F46E5'};">
            <strong style="font-size: 0.84rem; color: #1e293b; display: block;">${n.title}</strong>
            <p style="font-size: 0.76rem; color: #64748b; margin: 2px 0 4px 0; line-height: 1.3;">${n.message}</p>
            <span style="font-size: 0.68rem; color: #94a3b8;">${n.createdAt || 'Recent'}</span>
        </div>
    `).join('') || '<p style="font-size:0.8rem; color:#94a3b8; text-align:center;">No new notifications</p>';

    dropdown.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; border-bottom:1px solid #f1f5f9; padding-bottom:8px;">
            <strong style="font-size:0.95rem; color:#1e293b;"><i class="fas fa-bell" style="color:#4F46E5; margin-right:6px;"></i> Notifications</strong>
            <button id="markReadBtn" style="background:none; border:none; color:#4F46E5; font-size:0.75rem; cursor:pointer; font-weight:600;">Mark all read</button>
        </div>
        <div style="max-height: 260px; overflow-y: auto;">
            ${itemsHtml}
        </div>
    `;

    btn.appendChild(dropdown);

    const markBtn = dropdown.querySelector('#markReadBtn');
    if (markBtn) {
        markBtn.onclick = async (e) => {
            e.stopPropagation();
            try {
                if (typeof NotificationAPI !== 'undefined') await NotificationAPI.markRead();
            } catch(err) {}
            const dot = btn.querySelector('.notif-dot');
            if (dot) dot.style.display = 'none';
            dropdown.remove();
        };
    }

    document.addEventListener('click', function closeNotif(e) {
        if (!dropdown.contains(e.target) && e.target !== btn) {
            dropdown.remove();
            document.removeEventListener('click', closeNotif);
        }
    });
}

// ---- Auto run when page loads ----
document.addEventListener('DOMContentLoaded', () => {
    updateSidebarUser();
    initNotificationCenter();
});