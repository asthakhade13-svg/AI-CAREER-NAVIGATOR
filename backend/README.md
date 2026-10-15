# 🚀 AI Career Navigator

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4.0-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Grok API](https://img.shields.io/badge/Grok%20API-xAI%20LLM-000000?style=flat&logo=x&logoColor=white)](https://console.x.ai/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Pro-4285F4?style=flat&logo=google&logoColor=white)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%20%7C%20MongoDB-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-50%2F50%20(100%25)-success?style=flat&logo=pytest&logoColor=white)](#-automated-testing-suite)
[![Frontend](https://img.shields.io/badge/Frontend-GitHub%20Pages-222222?style=flat&logo=github&logoColor=white)](https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/)
[![Backend](https://img.shields.io/badge/Backend-Railway-0B0D0E?style=flat&logo=railway&logoColor=white)](https://railway.app/)

> An enterprise-grade, AI-driven career guidance, skill acceleration, and cryptographic credentialing platform tailored for Computer Science undergraduates, engineering students, and first-generation tech professionals.

---

## 🔗 Live Application & Portals

| Portal | URL | Description |
| :--- | :--- | :--- |
| 🌐 **Live Web Application** | [asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR](https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/) | Public Single-Page Application & Student Hub |
| 📚 **Interactive Swagger API** | [ai-career-navigator-production-b369.up.railway.app/docs](https://ai-career-navigator-production-b369.up.railway.app/docs) | OpenAPI 3.0 Documentation & Live API Playground |
| 🛡️ **Recruiter Credential Verifier** | [asthakhade13-svg.github.io/.../verify.html](https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/verify.html?certId=CN-2026-AIML-783E4B) | Public Cryptographic Verification Ledger |
| 👤 **Public Student Showcase** | [asthakhade13-svg.github.io/.../portfolio.html](https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/portfolio.html?studentId=user_001) | Shareable Recruiter Portfolio & Capstones |

---

## 🌟 Comprehensive Platform Capabilities

### 1. 🧠 Scientific Psychometrics & ML Recommendation Engine
* **Holland Codes (RIASEC) & Big Five Integration**: Diagnostic assessment analyzing **11 cognitive & personality traits** (*Analytical Thinking, Creativity, Curiosity, Attention to Detail, Communication, Leadership, Building Mindset, Research Mindset, User Empathy, Problem Solving, Technical Depth*).
* **3-Layer Diagnostic Matrix**:
  * **Layer 1 (50%)**: Personality & Cognitive Aptitude dimensions.
  * **Layer 2 (30%)**: Career Ambitions (*Placement, Technical Depth, Research, Entrepreneurship, Leadership*).
  * **Layer 3 (20%)**: Baseline Technical Exposure (*Programming rating, known languages, projects, Git/GitHub*).
* **Trained Random Forest Predictor**: Trained on **19,718 student profiles** to recommend optimal matches across **10 core CS specializations**: *AI/ML, Data Science, Cybersecurity, Web Engineering, Mobile Apps, Cloud & DevOps, UI/UX Product Design, Game Dev, Embedded Systems, and Software Engineering*.
* **Dynamic Adaptive Quiz Engine**:
  * 1,600+ multi-difficulty questions across 100+ CS sub-topics.
  * Real-time calibrated difficulty adjustments (*Easy, Medium, Hard*).
  * Automated option shuffling to prevent assessment bias.
  * Granular per-question time-tracking analytics and **Review Mistakes Modal** with remediation links.

---

### 2. 🗺️ Milestone Roadmaps, Code Runner & Direct Certificate Claim
* **Milestone Progress Tracking**: Interactive step-by-step curriculum milestones with subtask checkboxes and cloud synchronization.
* **Custom Personal Goals**: Add, check off, and delete personal study goals within any roadmap track.
* **Personal Milestone Notes**: Markdown-supported scratchpad per milestone stage to record reference documentation, code snippets, and study reflections.
* **Embedded Sandbox Code Runner**: Live multi-language code scratchpad powered by `POST /api/v1/roadmap/run-code` executing code with sandboxed `stdout`, `stderr`, and runtime benchmarks.
* **100% Roadmap Completion Banner**: Automatically detects 100% milestone completion and unlocks an instant **"Claim Specialization Certificate"** trigger (`POST /api/v1/roadmap/claim-certificate`).
* **Printable Track Syllabus PDF**: Export complete track curriculum to formal printable PDF.

---

### 3. 🤖 AI Mentor Chatbot (Audio TTS & Context-Aware Memory)
* **Multi-LLM Backend**: Powered by **xAI Grok** and **Google Gemini** for intelligent career counseling, technical doubt clarification, and interview prep.
* **Voice Speech Input & Transcription**: Voice recording with backend server-side audio transcription (`POST /api/v1/chatbot/transcribe-voice`).
* **Web Speech Synthesis Audio TTS**: Mentor answers read out loud via the browser's native Speech Synthesis API, featuring animated voice waves and an auto-speak toggle.
* **Context-Aware Roadmap Memory**: Chatbot queries `GET /api/v1/chatbot/roadmap-context/{student_id}` to detect which milestone the student is currently stuck on, providing tailored hints and practice challenges.
* **In-Chat Code Sandbox**: Sandboxed code execution window embedded directly inside mentor messages to run and test AI-suggested code snippets.
* **Persistent Chat History**: Full conversation threads preserved in SQLite database (`chat_history`).

---

### 4. 🏆 Gamification, Analytics & Productivity
* **Dynamic Real-User Leaderboard**: Real-time ranking based on curriculum progress, quiz scores, and study streak percentiles.
* **Study Stopwatch & Pomodoro Logger**: Integrated study timer logging session duration, sub-topic categorization (Coding, Projects, Reading, Assessments), and personal study notes.
* **Weekly Study Target Tracker**: Set customized weekly hour targets with live completion percentage visualizers.
* **Achievement Badges Engine**: Unlocks dynamic gamified credentials including:
  * 👑 *Consistency King* (active weekly streaks)
  * 📄 *ATS Pro* (resume scans above 80%)
  * 🛠️ *Capstone Finisher* (approved repositories)
  * 🎓 *Certified Specialist* (verified track credentials)
* **Automated Weekly Progress Digest**: Outbound SMTP email generator sending weekly performance summaries and upcoming goals.
* **Data Portability**: 1-click server-side CSV data export (`GET /api/v1/progress/export-csv/{student_id}`).
* **Notification Center**: Real-time notifications with batch mark-all-read capability.

---

### 5. 📄 Resume ATS Scanner & Tech Internships Portal
* **Resume ATS Scanner**:
  * Semantic keyword density and industry gap detection.
  * Instant ATS compatibility score (0–100%) and actionable formatting suggestions.
  * Historical scan ledger with score trajectory tracking.
* **Curated Internships Portal (`internships.html`)**:
  * Filter opportunities by **Remote**, **Minimum Stipend**, and **Location**.
  * **Live RSS Web Scraper** continuously ingesting active listings from top developer job feeds.
  * **Application Tracker**: Saved bookmarks and stage pipeline (*Applied, Interviewing, Offered, Rejected*).
  * **1-Click Application Modal**: Instant application dispatch with automatic resume attachment.
  * **AI Cover Letter Generator**: Generates customized cover letters tailored to the candidate's skills and target job description.

---

### 6. 👤 Public Student Showcase & Recruiter Portfolio (`portfolio.html`)
* **Shareable Candidate URL** (`/portfolio/{student_id}`): Publicly accessible showcase designed specifically for talent recruiters and hiring managers.
* **Verified Credentials Showcase**: Live verification status, score percentiles, and issuing authority.
* **Mentor-Reviewed GitHub Capstones**: Displays student repositories with mentor review notes and technical stack badges.
* **Gamification Trophy Shelf**: Unlocked badges, weekly streaks, and total hours logged.
* **Portfolio Customization**: Allows students to toggle public visibility of individual projects, certificates, and metrics (`POST /api/v1/portfolio/customize`).

---

### 7. 🛡️ Recruiter Verification & Official LinkedIn Certification (`verify.html`)
* **Tamper-Proof Cryptographic Ledger**: Every certificate is stamped with an immutable **SHA-256 cryptographic verification hash**.
* **1-Click "Add to LinkedIn Profile"**:
  * Direct integration launching LinkedIn's official Certification flow pre-filled with:
    * `startTask=CERTIFICATION_NAME`
    * Certification Title (e.g., *AI & Machine Learning Specialization Certificate of Completion*)
    * Issuing Organization (*AI Career Navigator*)
    * Issue Date & Credential ID
    * Public Verification URL
* **Social Share Preview Modal (`#sharePreviewModal`)**:
  * Rich OpenGraph social card preview showing verification badge and tamper-proof ledger status.
  * One-click share actions: **LinkedIn Add**, **LinkedIn Feed**, **X / Twitter Post**, and **GitHub Markdown Badge Embed**.
* **High-Resolution PNG Export (1920×1080 Full HD)**:
  * Pure client-side HTML5 Canvas rasterization (zero external library or CORS dependencies).
  * Rendered with ornamental navy & gold borders, central watermark, gold accreditation seal, competencies pills, and curriculum director signature.
* **Print-Ready PDF Certificate**: Official printable certificate equipped with a recruiter verification QR code.

---

### 8. 🔒 Security, Identity & Accessibility
* **Authentication Engine**: JWT Bearer token authentication, registration, login, and profile management.
* **Google One-Tap & OAuth 2.0**: Seamless single-click Google authentication with automated profile creation (`GET /api/v1/auth/google/url`, `POST /api/v1/auth/google/callback`).
* **Interactive Forgot Password Flow**: Outbound SMTP email delivery of 6-digit OTP codes with 60-second live cooldown timer.
* **Two-Factor Authentication (2FA)**: TOTP authenticator app QR setup, validation, recovery backup codes, and 2FA revocation.
* **Multi-Device Session Management**: Inspect active browser sessions with 1-click remote session revocation.
* **GDPR Data Portability & Account Deletion**: Export all student data in sanitized JSON or ZIP archive formats; cascading account deletion.
* **Real-Time WebSockets Peer Study Rooms**: Live study rooms with peer presence and collaborative study tracking (`/ws/study-room/{room_id}`).
* **Universal Dark Mode Theme Toggle**: Sun/moon toggle in the topbar across all pages with high-contrast `[data-theme="dark"]` CSS variables and multi-device cloud preference sync.
* **Server-Side Omnisearch Index**: Unified global search across roadmap milestones, career domains, internships, and tools.
* **Tech Hackathons & Events**: Upcoming hackathons calendar with `.ics` calendar exports and automated reminders.

---

## 🏗️ System Architecture

```
                                  ┌────────────────────────────────┐
                                  │   Student Diagnostic Inputs    │
                                  │ (Personality, Goals, Skills)   │
                                  └───────────────┬────────────────┘
                                                  │
                                                  ▼
                                  ┌────────────────────────────────┐
                                  │   11-Trait Extraction Engine   │
                                  │    (RIASEC + Big Five Map)     │
                                  └───────────────┬────────────────┘
                                                  │
                         ┌────────────────────────┴────────────────────────┐
                         ▼                                                 ▼
        ┌────────────────────────────────┐                ┌────────────────────────────────┐
        │   Random Forest ML Predictor   │                │   Adaptive Assessment Engine   │
        │   (Domain Career Suitability)  │                │   (Multi-Difficulty Testing)   │
        └────────────────┬───────────────┘                └────────────────┬───────────────┘
                         │                                                 │
                         └────────────────────────┬────────────────────────┘
                                                  │
                                                  ▼
        ┌──────────────────────────────────────────────────────────────────────────┐
        │                       AI Career Navigator Core API                       │
        │  ┌────────────────────┬────────────────────┬──────────────────────────┐  │
        │  │  Milestone Roadmap │  AI Mentor Chatbot │  Tech Internships Portal │  │
        │  │  & Code Sandbox    │  (Audio TTS + LLM) │  & RSS Scraper / ATS     │  │
        │  ├────────────────────┼────────────────────┼──────────────────────────┤  │
        │  │  Gamification &    │  Public Recruiter  │  Cryptographic Verifier  │  │
        │  │  Leaderboard       │  Student Portfolio │  (LinkedIn 1-Click + PNG)│  │
        │  └────────────────────┴────────────────────┴──────────────────────────┘  │
        └─────────────────────────────────────────┬────────────────────────────────┘
                                                  │
                                                  ▼
                                  ┌────────────────────────────────┐
                                  │  SQLite3 / MongoDB Atlas Store │
                                  │  (Persistent Student Ledger)   │
                                  └────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, Vanilla JavaScript (ES6+), Modern CSS3 (Glassmorphism, Dark Mode Variables), FontAwesome 6.5, Canvas 2D |
| **Backend API** | Python 3.11+, FastAPI, Starlette, Uvicorn, Pydantic v2 |
| **Machine Learning** | Scikit-Learn (Random Forest Classifier), Joblib, NumPy, Pandas |
| **LLMs & AI** | xAI Grok API, Google Gemini Pro API, SpeechSynthesis API |
| **Security & Auth** | JWT (PyJWT), Passlib (Bcrypt), PyOTP (2FA TOTP), Google OAuth 2.0 |
| **Databases** | SQLite3 (Zero-downtime local persistence), MongoDB / Atlas (pymongo) |
| **Networking & Realtime** | WebSockets, Outbound SMTP (Email OTP & Digests), Feedparser (RSS) |
| **Testing** | Comprehensive Automated Verification Suite (50 integration test suites) |
| **Deployment** | GitHub Pages (Frontend), Railway / Render (Cloud API Backend) |

---

## 🔌 API Endpoints Reference

### 🔐 Authentication & Account Security
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new student profile |
| `POST` | `/api/v1/auth/login` | Authenticate and issue JWT token |
| `GET`  | `/api/v1/auth/me` | Fetch authenticated student profile |
| `GET`  | `/api/v1/auth/google/url` | Get Google OAuth 2.0 consent URL |
| `POST` | `/api/v1/auth/google/callback` | Authenticate Google OAuth / One-Tap credential |
| `POST` | `/api/v1/auth/forgot-password` | Dispatch 6-digit OTP reset code via SMTP |
| `POST` | `/api/v1/auth/reset-password` | Reset password using valid OTP code |
| `POST` | `/api/v1/auth/2fa/setup` | Generate TOTP secret and QR code |
| `POST` | `/api/v1/auth/2fa/verify` | Verify TOTP code and enable 2FA |
| `POST` | `/api/v1/auth/2fa/disable` | Disable 2FA with password confirmation |
| `GET`  | `/api/v1/auth/sessions` | List active user device sessions |
| `POST` | `/api/v1/auth/sessions/revoke-all` | Revoke all other active sessions |
| `GET`  | `/api/v1/auth/export-archive/{id}` | Export GDPR-compliant archive (JSON or ZIP) |
| `DELETE`| `/api/v1/auth/account` | Cascading account deletion |

### 🧠 Psychometrics & Adaptive Quiz
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET`  | `/api/v1/basic_info/questions` | 19-question diagnostic assessment questionnaire |
| `GET`  | `/api/v1/basic_info/career_fields` | All 10 CS career specialization tracks |
| `POST` | `/api/v1/basic_info/evaluate` | Predict top matching career specializations |
| `POST` | `/api/v1/quiz/adaptive/start` | Initialize dynamic adaptive quiz session |
| `POST` | `/api/v1/quiz/adaptive/answer` | Submit answer and calibrate next question |
| `POST` | `/api/v1/quiz/log-attempt` | Log granular per-question timing analytics |
| `GET`  | `/api/v1/quiz/history/{student_id}`| Retrieve quiz attempt performance history |

### 🗺️ Roadmap, Code Runner & Milestone Notes
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/roadmap/generate` | Generate milestone-based learning roadmap |
| `POST` | `/api/v1/roadmap/toggle-subtask` | Check or uncheck a roadmap subtask |
| `POST` | `/api/v1/roadmap/custom-task` | Add custom student roadmap subtask |
| `DELETE`| `/api/v1/roadmap/custom-task` | Remove custom roadmap subtask |
| `POST` | `/api/v1/roadmap/milestone-note` | Save milestone markdown scratchpad note |
| `GET`  | `/api/v1/roadmap/milestone-notes/{student_id}` | Fetch student's milestone notes |
| `POST` | `/api/v1/roadmap/run-code` | Execute code snippet in sandboxed runner |
| `POST` | `/api/v1/roadmap/claim-certificate` | Direct certificate claim upon 100% completion |
| `GET`  | `/api/v1/roadmap/export-syllabus-pdf/{track}` | Export track syllabus to PDF |

### 🤖 AI Mentor Chatbot
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/chatbot/chat` | Send message to AI Mentor with memory |
| `POST` | `/api/v1/chatbot/transcribe-voice` | Transcribe voice recording audio |
| `GET`  | `/api/v1/chatbot/roadmap-context/{student_id}` | Retrieve student's current milestone context |
| `POST` | `/api/v1/chatbot/run-code` | Execute code snippet inside chatbot sandbox |

### 🛡️ Credential Verification & LinkedIn Accreditation
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/certificates/generate` | Generate cryptographically signed certificate |
| `GET`  | `/api/v1/certificates/verify/{cert_id}` | Public cryptographic verification lookup |
| `GET`  | `/api/v1/certificates/user/{student_id}` | Retrieve all student certificates |
| `GET`  | `/api/v1/certificates/share-payload/{cert_id}` | Pre-formatted LinkedIn 1-click & feed URLs |
| `GET`  | `/api/v1/certificates/share-card/{cert_id}` | Structured social embed card metadata |
| `GET`  | `/api/v1/certificates/download-pdf/{cert_id}` | Printable PDF with recruiter QR code |

### 💼 Tech Internships & ATS Scanner
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET`  | `/api/v1/internships/listings` | Filter internships (remote, stipend, location) |
| `POST` | `/api/v1/internships/bookmark` | Bookmark / save internship opportunity |
| `POST` | `/api/v1/internships/apply-status` | Update application status in pipeline |
| `POST` | `/api/v1/internships/apply-one-click` | Submit 1-click internship application |
| `POST` | `/api/v1/internships/generate-cover-letter` | Generate AI-tailored cover letter |
| `POST` | `/api/v1/resume/scan-text` | Parse resume text for ATS score and gaps |

### 👤 Public Showcase & Capstone Projects
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET`  | `/api/v1/portfolio/{student_id}` | Fetch public portfolio achievements & stats |
| `POST` | `/api/v1/portfolio/customize` | Update portfolio visibility and theme settings |
| `POST` | `/api/v1/projects/review-feedback` | Submit mentor/peer review notes on capstone |
| `GET`  | `/api/v1/projects/reviews/{student_id}/{project_id}` | Retrieve capstone reviews |

### 📊 Progress, Analytics & Omnisearch
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/progress/study-log` | Log study session timer with categories |
| `GET`  | `/api/v1/progress/badges/{student_id}` | Retrieve unlocked achievement badges |
| `POST` | `/api/v1/progress/weekly-target` | Set weekly study hours target |
| `GET`  | `/api/v1/progress/export-csv/{student_id}` | Export study records as CSV |
| `GET`  | `/api/v1/dashboard/search` | Unified global omnisearch index |
| `GET`  | `/api/v1/dashboard/events` | Tech hackathons and developer events |

---

## 🧪 Automated Testing Suite

The backend contains a rigorous, end-to-end automated testing suite with **50 comprehensive test suites**, validating all layers of the application:

```bash
# Run the complete test suite from the backend directory
cd backend
python test_all_features.py
```
```

---

## 💻 Local Development Setup

### 1. Prerequisites
* Python 3.11+
* Git
* Modern Web Browser (Chrome, Firefox, Edge, Safari)

### 2. Clone Repository
```bash
git clone https://github.com/asthakhade13-svg/AI-CAREER-NAVIGATOR.git
cd AI-CAREER-NAVIGATOR
```

### 3. Create & Activate Virtual Environment
```bash
# On Windows (PowerShell):
python -m venv backend/venv
backend/venv/Scripts/Activate.ps1

# On macOS/Linux:
python3 -m venv backend/venv
source backend/venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and populate your API credentials:
```env
PORT=8000
DEBUG=True
JWT_SECRET=your_super_secret_jwt_key
GROK_API_KEY=your_xai_grok_api_key
GEMINI_API_KEY=your_google_gemini_api_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@domain.com
SMTP_PASS=your_email_app_password
GOOGLE_CLIENT_ID=your_google_oauth_client_id
```

### 6. Run the Application
```bash
# Run server
cd backend
python app.py
```

* **Frontend Web App**: `http://localhost:8000/`
* **Swagger API Documentation**: `http://localhost:8000/docs`
* **Redoc Documentation**: `http://localhost:8000/redoc`

---

## 📁 Repository Structure

```
AI-CAREER-NAVIGATOR/
├── index.html                   # Landing page & 3-layer diagnostic assessment
├── dashboard.html               # Main student analytics & progress hub
├── roadmap.html                 # Milestone roadmap, scratchpad & code runner
├── chatbot.html                 # AI Mentor with TTS voice & roadmap memory
├── quiz.html                    # Adaptive testing & mistake review engine
├── internships.html             # Tech internships portal & 1-click apply
├── portfolio.html               # Public student showcase & recruiter portfolio
├── verify.html                  # Credential verification & LinkedIn 1-click add
├── login.html                   # Auth with Google One-Tap & SMTP OTP reset
├── register.html                # Student onboarding & account creation
├── settings.html                # Security, 2FA, session revocation & preferences
├── api.js                       # Comprehensive client-side API SDK
├── style.css / dashboard.css    # Responsive styles with dark mode CSS variables
│
├── backend/
│   ├── app.py                   # FastAPI application & route mounting
│   ├── config.py                # Configuration settings & environment loader
│   ├── database.py              # SQLite & MongoDB database interfaces
│   ├── test_all_features.py     # 50/50 Comprehensive automated test suite
│   ├── routes/                  # Modular FastAPI routers
│   │   ├── auth_routes.py       # Authentication, 2FA, GDPR & sessions
│   │   ├── basic_info_routes.py # 19-Question assessment endpoints
│   │   ├── certificate_routes.py# Verifiable credentials & LinkedIn payloads
│   │   ├── chatbot_routes.py    # LLM conversation & voice transcription
│   │   ├── internship_routes.py # Internships, RSS scraper & cover letters
│   │   ├── portfolio_routes.py  # Public recruiter showcase endpoints
│   │   ├── progress_routes.py   # Badges, study stopwatch & analytics
│   │   ├── quiz_routes.py       # Adaptive assessment engine
│   │   ├── roadmap_routes.py    # Roadmaps, code runner & milestone notes
│   │   └── websocket_routes.py  # Real-time peer study room sockets
│   ├── services/                # Business logic & ML integrations
│   │   ├── auth_service.py      # SQLite tables, password hashing & JWT
│   │   ├── certificate_service.py# Cryptographic signatures & SHA-256
│   │   ├── chatbot_service.py   # LLM orchestration (Grok / Gemini)
│   │   └── ml_service.py        # Random Forest model inference
│   └── data/                    # Datasets & Questionnaires
│       ├── basic_info_questions.csv # 19-Question assessment dataset
│       └── career_nav.db        # SQLite persistence database
│
└── frontend/                    # Synchronized static mirror for GitHub Pages
```

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  Built with ❤️ for first-generation engineers & computer science students worldwide.<br/>
  <b>AI Career Navigator Accreditation Board © 2026</b>
</p>
