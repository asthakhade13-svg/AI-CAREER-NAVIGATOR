# First-Generation Career Navigator AI Backend

An AI-powered career guidance platform backend for 1st Year B.Tech Computer Science students, especially first-generation learners.

## Features
- Read learning materials from CSV files
- Automatically generate quizzes using Gemini API
- Evaluate student quiz responses
- Analyze student skills and detect gaps
- Recommend suitable Computer Science career paths using Scikit-Learn
- Generate personalized learning roadmaps
- Store and retrieve student progress (MongoDB)
- Provide an AI mentor chatbot API

## Tech Stack
- Python 3.11+
- FastAPI
- MongoDB
- Pandas, NumPy, Scikit-Learn
- Google Gemini API

## Project Structure

```
backend/
├── data/
│   ├── career_paths.json
│   ├── industry_skills.json
│   ├── learning_materials.csv
│   └── sample_students.csv
├── models/
│   ├── progress_model.py
│   ├── quiz_evaluation_model.py
│   ├── recommendation_model.py
│   └── skill_gap_model.py
├── routes/
│   ├── chatbot_routes.py
│   ├── progress_routes.py
│   ├── quiz_routes.py
│   ├── recommendation_routes.py
│   └── roadmap_routes.py
├── services/
│   ├── career_recommender.py
│   ├── chatbot_service.py
│   ├── quiz_evaluator.py
│   ├── quiz_generator.py
│   ├── roadmap_generator.py
│   └── skill_gap_analyzer.py
├── utils/
│   ├── constants.py
│   ├── csv_loader.py
│   ├── helpers.py
│   ├── text_preprocessing.py
│   └── validators.py
├── app.py
├── config.py
├── database.py
├── train_model.py
├── requirements.txt
└── .env.example
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Environment Variables:
   - Copy `.env.example` to `.env`
   - Add your `MONGODB_URI` and `GEMINI_API_KEY`

4. Train the ML Model (first time only):
   ```bash
   python train_model.py
   ```

5. Run the API:
   ```bash
   uvicorn app:app --reload
   ```

6. Access Swagger UI documentation:
   http://localhost:8000/docs
