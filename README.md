# AI Career Navigator

An AI-powered career guidance platform for computer science students, combining psychometric analysis, adaptive assessments, and machine learning to map personal traits to suitable career domains.

## 🔗 Live Links
* **Live Web Application (Frontend)**: [https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/](https://asthakhade13-svg.github.io/AI-CAREER-NAVIGATOR/)
* **Backend API & Docs (Railway)**: [https://ai-career-navigator-production-b369.up.railway.app/docs](https://ai-career-navigator-production-b369.up.railway.app/docs)

## Key Features
* **Psychometric Mapping (RIASEC & Big Five)**: Combines Holland Codes (RIASEC) and the Big Five Personality frameworks to analyze 11 cognitive/personality traits.
* **Dual-Layer Assessment**: 
  * *Diagnostic Stage*: Evaluates personality, goals, and technical exposure.
  * *Adaptive Quiz*: Generates dynamic, multi-difficulty questions matching the student's CS or general readiness tier.
* **Random Forest ML Predictor**: Trained on 19,000+ records from OpenPsychometrics to classify top career paths with 100% validation fit and robust centroid-based fallback.
* **Skill Gap & Roadmap Generator**: Automated evaluation comparing current student knowledge against target domain demands, producing customized learning roadmaps.
* **AI Mentor Chatbot**: Real-time LLM-driven mentoring interface to guide students on skill acquisition and learning resources.
* **Modern Interface**: Glassmorphic, responsive UI with interactive timeline roadmap rendering and dynamic chat views.

---

## Technology Stack
* **Backend**: FastAPI, Python, Uvicorn
* **Machine Learning**: Scikit-Learn, Joblib, Pandas, NumPy
* **Frontend**: HTML5, Vanilla JavaScript, CSS3
* **AI/LLM**: Google Gemini API
* **Database**: MongoDB

---

## Getting Started

### 1. Prerequisites & Environment Setup
Create a virtual environment and install the required dependencies:
```bash
# Initialize and activate venv
python -m venv venv
venv/Scripts/activate  # On macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the root and configure the following variables:
```env
MONGODB_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
```

### 2. Preprocess Data & Train ML Models
To download the OpenPsychometrics datasets, preprocess the traits, and train the Random Forest Classifier:
```bash
python train_model.py
```

### 3. Run the Server Locally
```bash
# Run FastAPI application
python app.py
```
Access the application locally:
* **Web App**: [http://localhost:8000/](http://localhost:8000/)
* **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

