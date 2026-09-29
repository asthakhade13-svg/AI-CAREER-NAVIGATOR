from typing import List, Optional

def generate_roadmap(target_domain: str, missing_skills: Optional[List[str]] = None, timeframe: Optional[str] = "6 Months", custom_prompt: Optional[str] = None) -> dict:
    """
    Generates a structured, rich learning roadmap with milestones, topics, and free resources.
    """
    missing = missing_skills or []
    dom_clean = target_domain.replace('_', ' ').title()

    if "ai" in target_domain.lower() or "ml" in target_domain.lower():
        steps = [
            {
                "title": "Python Programming & Math Foundations",
                "week": "Month 1 (Week 1–4)",
                "desc": "Master Python syntax, NumPy, Pandas, Linear Algebra, and Calculus fundamentals for data pipelines.",
                "topics": ["Python OOP & Iterators", "NumPy Vectorization", "Pandas DataFrames", "Matrix Multiplication & Gradients"],
                "resources": [
                    {"title": "Kaggle Python Course", "type": "Interactive", "url": "https://www.kaggle.com/learn/python"},
                    {"title": "3Blue1Brown Essence of Linear Algebra", "type": "Video", "url": "https://www.youtube.com/@3blue1brown"}
                ],
                "status": "done"
            },
            {
                "title": "Classical Machine Learning Algorithms",
                "week": "Month 2 (Week 5–8)",
                "desc": "Understand regression, decision trees, random forests, SVMs, and scikit-learn evaluation metrics.",
                "topics": ["Supervised vs Unsupervised Learning", "Cross-Validation & GridSearch", "Hyperparameter Tuning", "Scikit-Learn Workflows"],
                "resources": [
                    {"title": "Andrew Ng Machine Learning Specialization", "type": "Course", "url": "https://www.coursera.org"},
                    {"title": "StatQuest ML Fundamentals", "type": "Video", "url": "https://www.youtube.com/@statquest"}
                ],
                "status": "active"
            },
            {
                "title": "Deep Learning & Neural Architectures",
                "week": "Month 3 (Week 9–12)",
                "desc": "Build neural networks with PyTorch, understand backpropagation, activation functions, and CNNs/RNNs.",
                "topics": ["PyTorch Tensors & Autograd", "Loss Functions & Optimizers", "CNNs for Computer Vision", "Transformers Basics"],
                "resources": [
                    {"title": "Fast.ai Practical Deep Learning", "type": "Course", "url": "https://course.fast.ai"},
                    {"title": "PyTorch Official Tutorials", "type": "Docs", "url": "https://pytorch.org/tutorials"}
                ],
                "status": "locked"
            },
            {
                "title": "Generative AI, RAG & LLM Deployment",
                "week": "Month 4–5 (Week 13–20)",
                "desc": "Develop RAG pipelines with vector databases (FAISS/Chroma), LangChain, and deploy FastAPI endpoints.",
                "topics": ["Embeddings & Vector Search", "LangChain & LlamaIndex", "Prompt Engineering", "FastAPI Serving & Docker"],
                "resources": [
                    {"title": "DeepLearning.AI LangChain Guide", "type": "Interactive", "url": "https://www.deeplearning.ai"},
                    {"title": "Hugging Face NLP Course", "type": "Course", "url": "https://huggingface.co/learn"}
                ],
                "status": "locked"
            }
        ]
    else:
        steps = [
            {
                "title": f"{dom_clean} Core Foundations",
                "week": "Month 1 (Week 1–4)",
                "desc": f"Understand core architecture, essential syntax, and tooling for modern {dom_clean}.",
                "topics": ["Foundational Theory", "Development Environment Setup", "Version Control with Git", "Core Syntax"],
                "resources": [
                    {"title": f"{dom_clean} MDN / Official Documentation", "type": "Docs", "url": "https://developer.mozilla.org"},
                    {"title": "FreeCodeCamp Complete Course", "type": "Course", "url": "https://www.freecodecamp.org"}
                ],
                "status": "done"
            },
            {
                "title": "Intermediate Architecture & State Management",
                "week": "Month 2–3 (Week 5–12)",
                "desc": "Implement modular components, asynchronous API integration, and performance optimizations.",
                "topics": ["Component Lifecycle", "RESTful API Integration", "State Management", "Error Handling & Debugging"],
                "resources": [
                    {"title": "Roadmap.sh Developer Guides", "type": "Visual", "url": "https://roadmap.sh"},
                    {"title": "JavaScript.info Modern Tutorial", "type": "Tutorial", "url": "https://javascript.info"}
                ],
                "status": "active"
            },
            {
                "title": "Full-Stack Portfolio Projects & Testing",
                "week": "Month 4–5 (Week 13–20)",
                "desc": "Build 2 production-grade full-stack capstone projects with unit tests and continuous deployment.",
                "topics": ["Project Architecture", "Unit & Integration Testing", "CI/CD Deployment", "Database Modeling"],
                "resources": [
                    {"title": "Full Stack Open (University of Helsinki)", "type": "Course", "url": "https://fullstackopen.com"},
                    {"title": "GitHub Student Developer Pack", "type": "Tools", "url": "https://education.github.com/pack"}
                ],
                "status": "locked"
            }
        ]

    if custom_prompt and len(custom_prompt.strip()) > 3:
        # Dynamically inject custom focus module based on student prompt
        p_clean = custom_prompt.strip()
        custom_step = {
            "title": f"🎯 Custom Focus: {p_clean[:45]}...",
            "week": "Accelerated Focus Sprint",
            "desc": f"Tailored module generated for your goal: '{p_clean}'. Prioritizes fast-track practical mastery and targeted project deliverables.",
            "topics": [
                f"Core Deep-Dive: {p_clean[:30]}",
                "Hands-on Implementation & Code Sandbox",
                "Portfolio Integration & Architecture Review",
                "Mock Technical Assessment & Deployment"
            ],
            "resources": [
                {"title": f"{p_clean[:30]} Curated Deep-Dive", "type": "Interactive", "url": "https://roadmap.sh"},
                {"title": "Open Source Project Sandbox", "type": "GitHub", "url": "https://github.com/topics"}
            ],
            "status": "active"
        }
        # Place custom focus step as high priority
        steps.insert(1, custom_step)

    return {
        "domain": target_domain,
        "title": f"{dom_clean} AI Roadmap",
        "timeframe": timeframe,
        "customPrompt": custom_prompt or "Standard Track Progression",
        "totalSteps": len(steps),
        "steps": steps
    }
