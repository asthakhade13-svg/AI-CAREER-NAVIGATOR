import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

PROJECT_BLUEPRINTS = {
    "aiml": [
        {
            "id": "proj_aiml_rag",
            "title": "Autonomous Multi-Document RAG Knowledge Assistant",
            "difficulty": "Intermediate",
            "duration": "2 - 3 Weeks",
            "track": "AI / Machine Learning",
            "description": "Build an end-to-end Retrieval-Augmented Generation (RAG) system with hybrid semantic search, vector embeddings (FAISS/ChromaDB), and local LLM inference.",
            "techStack": ["Python", "FastAPI", "LangChain / LlamaIndex", "FAISS", "HuggingFace", "Streamlit / React"],
            "architecture": "Client UI -> FastAPI Gateway -> Hybrid Retriever (Dense Embeddings + BM25) -> Vector DB -> LLM Context Synthesizer -> Streaming Response",
            "folderStructure": """rag-assistant/
├── backend/
│   ├── app.py
│   ├── services/
│   │   ├── document_parser.py
│   │   ├── vector_store.py
│   │   └── rag_engine.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   └── app.js
├── data/
│   └── documents/
└── README.md""",
            "milestones": [
                "Step 1: Ingest and chunk PDF/Markdown documents with overlap",
                "Step 2: Generate sentence embeddings and store in FAISS index",
                "Step 3: Construct prompt templates with retrieved context and citations",
                "Step 4: Build FastAPI streaming endpoints and simple web chat interface"
            ],
            "resumeBulletPoint": "Architected an end-to-end RAG system indexing 500+ research papers with FAISS and FastAPI, reducing query retrieval latency by 45%."
        },
        {
            "id": "proj_aiml_cv",
            "title": "Real-Time Edge Computer Vision & Object Tracking Pipeline",
            "difficulty": "Advanced",
            "duration": "3 Weeks",
            "track": "AI / Machine Learning",
            "description": "Develop a lightweight real-time object detection and tracking pipeline utilizing YOLOv8 and ByteTrack with FPS optimization.",
            "techStack": ["Python", "OpenCV", "YOLOv8", "PyTorch", "ONNX Runtime"],
            "architecture": "Video Stream -> Frame Preprocessor -> YOLOv8 ONNX Model -> ByteTrack Associator -> Annotated Output Display",
            "folderStructure": """vision-tracker/
├── src/
│   ├── detector.py
│   ├── tracker.py
│   └── video_stream.py
├── models/
│   └── yolov8n.onnx
├── tests/
└── main.py""",
            "milestones": [
                "Step 1: Set up OpenCV video capture pipeline with frame skipping",
                "Step 2: Export PyTorch YOLOv8 weights to ONNX format for 2x inference speedup",
                "Step 3: Integrate multi-object tracking algorithm (DeepSORT or ByteTrack)",
                "Step 4: Benchmark frame rates (FPS) and precision metrics (mAP@50)"
            ],
            "resumeBulletPoint": "Developed real-time computer vision tracking pipeline in PyTorch/ONNX achieving 38+ FPS on consumer hardware."
        }
    ],
    "uiux": [
        {
            "id": "proj_uiux_fintech",
            "title": "Accessible FinTech Micro-Savings App & Design System",
            "difficulty": "Beginner - Intermediate",
            "duration": "2 Weeks",
            "track": "UI/UX & Product Design",
            "description": "End-to-end mobile UX case study designing a micro-investing experience for first-generation students, complete with Figma design tokens and WCAG AA accessibility audit.",
            "techStack": ["Figma", "FigJam", "Design Tokens", "Maze (Usability Testing)", "Notion Case Study"],
            "architecture": "Empathy Mapping -> Persona Definition -> Low-Fi Wireframes -> Atomic Design System (Colors, Typography, Components) -> High-Fi Interactive Prototype -> Usability Feedback Loop",
            "folderStructure": """fintech-ux-case-study/
├── 01_research/
│   ├── user_interviews.pdf
│   └── competitive_audit.pdf
├── 02_wireframes/
│   └── user_flow_v1.png
├── 03_design_system/
│   ├── color_palette.tokens
│   └── components_figma_link.txt
└── 04_case_study_deck.pdf""",
            "milestones": [
                "Step 1: Conduct 5 user interviews with first-gen college students on budgeting habits",
                "Step 2: Map user journeys and identify core friction points in money onboarding",
                "Step 3: Build a 20+ component library in Figma utilizing Auto Layout and variants",
                "Step 4: Run usability testing with Maze and document iterations in a portfolio case study"
            ],
            "resumeBulletPoint": "Designed an accessibility-first FinTech mobile app in Figma with 25+ reusable design components, scoring 94% on usability testing."
        }
    ],
    "webdev": [
        {
            "id": "proj_webdev_saas",
            "title": "Full-Stack Collaborative Team Kanban & Workspace",
            "difficulty": "Intermediate",
            "duration": "2 - 3 Weeks",
            "track": "Web Development",
            "description": "Full-stack project management application with real-time drag-and-drop task reordering, JWT authentication, SQLite/PostgreSQL persistence, and live updates.",
            "techStack": ["JavaScript / TypeScript", "Node.js / FastAPI", "SQLite / PostgreSQL", "HTML5 Drag-and-Drop", "REST APIs"],
            "architecture": "Client Web App -> Auth Middleware -> REST Controller -> Service Layer -> ORM / SQL Database",
            "folderStructure": """kanban-workspace/
├── api/
│   ├── routes/
│   ├── models/
│   └── server.js
├── public/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── package.json""",
            "milestones": [
                "Step 1: Design database schema for Users, Workspaces, Boards, and Cards",
                "Step 2: Implement secure token-based authentication and route guards",
                "Step 3: Build responsive Kanban UI with fluid drag-and-drop interactions",
                "Step 4: Implement optimistic UI updates and error recovery"
            ],
            "resumeBulletPoint": "Built full-stack collaborative workspace supporting drag-and-drop task boards with JWT auth and sub-50ms API response times."
        }
    ],
    "cyber": [
        {
            "id": "proj_cyber_scanner",
            "title": "Automated Web Vulnerability Scanner & Security Auditor",
            "difficulty": "Intermediate",
            "duration": "2 Weeks",
            "track": "Cybersecurity",
            "description": "CLI & Web security tool that scans target endpoints for OWASP Top 10 vulnerabilities including SQL injection patterns, missing security headers, and open ports.",
            "techStack": ["Python", "Requests", "BeautifulSoup", "Socket Programming", "Markdown Reporter"],
            "architecture": "Target URL -> Port & Header Scanner -> Payload Injection Tester -> Vulnerability Parser -> HTML/PDF Executive Report",
            "folderStructure": """sec-scanner/
├── scanner/
│   ├── port_scanner.py
│   ├── header_checker.py
│   └── sqli_detector.py
├── reports/
└── scanner_cli.py""",
            "milestones": [
                "Step 1: Develop multithreaded TCP port scanner with socket timeouts",
                "Step 2: Check for missing security headers (HSTS, CSP, X-Frame-Options)",
                "Step 3: Test endpoints with benign SQL injection and XSS payloads against mock vulnerable app",
                "Step 4: Generate automated security audit reports with severity ratings"
            ],
            "resumeBulletPoint": "Created automated vulnerability scanner in Python detecting 8+ common web misconfigurations and generating comprehensive audit reports."
        }
    ],
    "cloud": [
        {
            "id": "proj_cloud_cicd",
            "title": "Automated Multi-Environment CI/CD Infrastructure Pipeline",
            "difficulty": "Intermediate",
            "duration": "2 Weeks",
            "track": "Cloud & DevOps",
            "description": "Production-grade CI/CD pipeline with GitHub Actions, Docker containerization, health check testing, and zero-downtime deployment.",
            "techStack": ["Docker", "GitHub Actions", "AWS / Render / DigitalOcean", "Nginx", "Bash"],
            "architecture": "Git Push -> GitHub Action Workflow (Lint, Unit Test, Build Image) -> Container Registry -> Production Deploy -> Health Ping",
            "folderStructure": """devops-pipeline/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── Dockerfile
├── nginx.conf
├── src/
└── docker-compose.yml""",
            "milestones": [
                "Step 1: Write optimized multi-stage Dockerfile minimizing image size (<100MB)",
                "Step 2: Configure GitHub Actions workflow for automated testing on pull requests",
                "Step 3: Set up Nginx reverse proxy with SSL certificate termination",
                "Step 4: Implement automated health-check rollback strategy"
            ],
            "resumeBulletPoint": "Constructed automated CI/CD pipeline with GitHub Actions and multi-stage Docker builds, reducing deployment time to under 90 seconds."
        }
    ],
    "datascience": [
        {
            "id": "proj_ds_dashboard",
            "title": "Predictive Customer Churn Analysis & Interactive BI Dashboard",
            "difficulty": "Intermediate",
            "duration": "2 Weeks",
            "track": "Data Science",
            "description": "Perform comprehensive Exploratory Data Analysis on a 50k customer telecom dataset, train predictive churn classification models, and build an interactive Streamlit BI dashboard.",
            "techStack": ["Python", "Pandas", "Scikit-Learn", "Seaborn / Plotly", "Streamlit"],
            "architecture": "Raw CSV Data -> Pandas Data Cleaning Pipeline -> Feature Engineering -> Random Forest / XGBoost Model -> Streamlit Dashboard",
            "folderStructure": """churn-analytics/
├── notebooks/
│   └── eda_and_modeling.ipynb
├── dashboard/
│   └── app.py
├── data/
│   └── telecom_churn.csv
└── requirements.txt""",
            "milestones": [
                "Step 1: Clean raw data, handle missing values, and perform one-hot encoding",
                "Step 2: Conduct statistical correlation analysis and feature importance ranking",
                "Step 3: Train Random Forest classifier and evaluate ROC-AUC curve",
                "Step 4: Build interactive dashboard allowing stakeholders to simulate churn risk per customer"
            ],
            "resumeBulletPoint": "Engineered predictive churn model with 87% accuracy and built interactive Plotly/Streamlit dashboard for business risk analysis."
        }
    ]
}


def get_recommended_projects(track_key: str = "aiml") -> List[Dict[str, Any]]:
    track_key = track_key.lower().strip() if track_key else "aiml"
    if track_key in PROJECT_BLUEPRINTS:
        return PROJECT_BLUEPRINTS[track_key]
    
    # Check partial match
    for key, projects in PROJECT_BLUEPRINTS.items():
        if key in track_key or track_key in key:
            return projects
            
    return PROJECT_BLUEPRINTS["aiml"]
