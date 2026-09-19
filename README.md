# 🚀 AI Career Navigator

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4.0-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Grok API](https://img.shields.io/badge/Grok%20API-xAI%20LLM-000000?style=flat&logo=x&logoColor=white)](https://console.x.ai/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![GitHub Pages](https://img.shields.io/badge/Frontend-GitHub%20Pages-222222?style=flat&logo=github&logoColor=white)](https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/)
[![Railway](https://img.shields.io/badge/Backend-Railway-0B0D0E?style=flat&logo=railway&logoColor=white)](https://railway.app/)

An AI-powered career orientation and diagnostic assessment platform tailored for Computer Science students and first-generation learners. The platform fuses validated psychometric frameworks (**RIASEC Holland Codes** & **Big Five Personality Traits**) with **Machine Learning** and **Adaptive Testing** to recommend optimal career paths, detect skill gaps, and generate customized step-by-step learning roadmaps.

---

## 🔗 Live Links

* 🌐 **Live Web Application (Frontend)**: [https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/](https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/)
* 📚 **Backend API & Swagger Documentation**: [https://ai-career-navigator-production-b369.up.railway.app/docs](https://ai-career-navigator-production-b369.up.railway.app/docs)

---

## 🌟 Key Features

### 1. 🧠 Scientific Psychometric Profiling
* **Holland Codes (RIASEC) & Big Five Integration**: Evaluates **11 cognitive and personality traits** (*Analytical Thinking, Creativity, Curiosity, Attention to Detail, Communication, Leadership, Building Mindset, Research Mindset, User Empathy, Problem Solving, Technical Depth*).
* **3-Layer Diagnostic Matrix**:
  1. *Layer 1 (50%)*: Personality & Cognitive Aptitude traits.
  2. *Layer 2 (30%)*: Career Goals (Placement, Technical Depth, Research, Entrepreneurship, Leadership).
  3. *Layer 3 (20%)*: Baseline Technical Exposure (Programming rating, known languages, projects, Git/GitHub).

### 2. 🤖 Machine Learning Recommendation Engine
* **Trained Random Forest Classifier**: Trained on **19,718 clean student records** derived from OpenPsychometrics datasets to predict suitability across 10 core computer science domains.
* **Fallback Similarity Engine**: Implements Cosine Similarity and Softmax probability distributions across profile centroids for zero-downtime offline execution.
* **Target Career Domains**: *AI/ML, Data Science, Cyber Security, Web Development, App Development, UI/UX Design, Cloud Computing, DevOps, Game Development, Software Engineering*.

### 3. 🎯 Dynamic Adaptive Quiz
* **Intelligent Routing**: Automatically routes students to the *Foundation* or *CS Ready* track based on Layer 3 diagnostic scores.
* **Dynamic Multi-Difficulty Questioning**: Adjusts difficulty (*Easy, Medium, Hard*) in real time based on user performance across 1,600+ questions spanning 100+ CS sub-topics.
* **Automated Option Shuffling**: Implements randomized answer options to eliminate bias during assessments.

### 4. 🗺️ Personalized Roadmap & Skill Gap Analyzer
* **Skill Gap Identification**: Compares current student quiz competencies against industry requirements.
* **Step-by-Step Learning Timeline**: Generates a milestone-based learning roadmap complete with recommended topics, projects, and certifications.
* **AI Mentor Chatbot**: Real-time LLM-powered assistant (powered by **Grok API / Gemini**) to provide contextual career counseling, answers, and study strategies.

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
                                  ┌────────────────────────────────┐
                                  │ Skill Gap & Roadmap Generator  │
                                  │   + AI Mentor Chatbot (Grok)   │
                                  └────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, Modern CSS3 (Glassmorphism), Vanilla JavaScript, Chart.js |
| **Backend API** | Python 3.11+, FastAPI, Uvicorn, Pydantic v2 |
| **Machine Learning** | Scikit-Learn (Random Forest), Joblib, Pandas, NumPy |
| **LLM & AI** | Grok API (xAI) / Google Gemini API |
| **Database** | MongoDB / MongoDB Atlas (pymongo) |
| **Deployment** | GitHub Pages (Frontend) + Railway / Render (Cloud Backend) |

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/basic_info/questions` | Retrieves the 33-question diagnostic assessment questionnaire |
| `GET` | `/api/v1/basic_info/career_fields` | Returns all available career specialization domains |
| `POST`| `/api/v1/basic_info/evaluate` | Evaluates student profile & predicts top 3 matching career domains |
| `POST`| `/api/v1/quiz/adaptive/start` | Initializes a dynamic adaptive quiz session |
| `POST`| `/api/v1/quiz/adaptive/answer` | Submits an answer and returns the next calibrated question |
| `POST`| `/api/v1/recommend/recommend` | Runs the Random Forest classifier on quiz feature vectors |
| `POST`| `/api/v1/recommend/skill_gap` | Computes missing skills and technical readiness for a target domain |
| `POST`| `/api/v1/roadmap/generate` | Generates a structured, milestone-based learning roadmap |
| `POST`| `/api/v1/chatbot/chat` | AI Mentor conversation endpoint with student context |
| `GET` | `/health` | Cloud health check endpoint |

---

## 💻 Local Development Setup

### 1. Clone & Setup Environment
```bash
# Clone the repository
git clone https://github.com/asthakhade13-svg/AI-CAREER-NAVIGATOR.git
cd AI-CAREER-NAVIGATOR

# Create and activate virtual environment
python -m venv venv
venv/Scripts/activate  # On macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Application
```bash
# Start backend server with live reload
python app.py
```
* Access the Web App: **[http://localhost:8000/](http://localhost:8000/)**
* Interactive API Documentation (Swagger UI): **[http://localhost:8000/docs](http://localhost:8000/docs)**


