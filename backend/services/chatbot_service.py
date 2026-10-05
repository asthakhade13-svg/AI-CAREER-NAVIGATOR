import logging
import requests
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are an expert AI Career & Technical Mentor for engineering and computer science students.
Your mission is to provide clear, actionable, friendly, and structured guidance on:
- Learning roadmaps (UI/UX Design, AI/ML, Cybersecurity, Web Development, Data Science, Cloud/DevOps, Mobile App Dev)
- Technical explanations with clean code examples
- Resume, interview preparation, internship strategies, and portfolio building
- Step-by-step problem-solving approaches.

Format your responses with clear markdown, bullet points, and actionable next steps."""


def mentor_chat(student_id: str, message: str, custom_api_key: Optional[str] = None) -> str:
    """
    Generates a personalized AI Mentor response using Google Gemini, Groq, or an intelligent fallback expert system.
    """
    api_key = custom_api_key or settings.GEMINI_API_KEY or ""

    # Fetch live student context from SQLite
    context_addon = ""
    try:
        from services.auth_service import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT full_name, career_track, year, college, branch FROM users WHERE id = ? OR email = ?", (student_id, student_id))
        u = cursor.fetchone()
        if u:
            context_addon = f"\n\nStudent Profile: Name: {u['full_name']}, Specialization Track: {u['career_track']}, Year: {u['year']}, Branch: {u['branch']}, College: {u['college']}. Tailor your advice directly to their specialization and progress."
        conn.close()
    except Exception:
        pass

    full_system_instruction = SYSTEM_INSTRUCTION + context_addon

    # 1. Try Google Gemini REST API (v1beta gemini-1.5-flash)
    if api_key and not api_key.startswith("gsk_") and not api_key.startswith("xai-"):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "systemInstruction": {
                    "parts": [{"text": full_system_instruction}]
                },
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": message}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1000
                }
            }
            res = requests.post(url, headers=headers, json=payload, timeout=12)
            if res.ok:
                data = res.json()
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if text:
                    return text
            else:
                logger.warning(f"Gemini API returned {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")

    # 2. Try Groq API if key is present
    groq_key = api_key if api_key.startswith("gsk_") else settings.GROK_API_KEY
    if groq_key and groq_key.startswith("gsk_"):
        try:
            api_url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            res = requests.post(api_url, headers=headers, json=payload, timeout=10)
            if res.ok:
                return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")

    # 3. Intelligent Domain-Aware Built-in AI Mentor Engine (Fallback)
    return generate_intelligent_mentor_response(message)


def generate_intelligent_mentor_response(message: str) -> str:
    """
    Intelligent dynamic response generator when external API keys are unreachable.
    Provides structured, domain-specific mentorship for students.
    """
    msg = (message or "").lower()

    if any(k in msg for k in ["ui", "ux", "design", "figma", "wireframe"]):
        return (
            "🎨 **UI/UX & Product Design Guidance:**\n\n"
            "To break into UI/UX Design as a student:\n"
            "1. **Master Figma Core**: Learn Frames, Auto Layout, Component Variants, and Interactive Prototyping.\n"
            "2. **Design Foundations**: Understand visual hierarchy, the 8pt spacing grid, typography rules, and WCAG accessibility contrast.\n"
            "3. **Build 2 In-depth Case Studies**: Don't just show pretty mockups—document the problem, user research, wireframes, and usability testing.\n"
            "4. **Free Resources**: [Refactoring UI](https://www.refactoringui.com), [Figma Learn](https://help.figma.com), and [Nielsen Norman Group](https://www.nngroup.com)."
        )

    if any(k in msg for k in ["ai", "machine learning", "ml", "deep learning", "neural", "python"]):
        return (
            "🤖 **AI & Machine Learning Roadmap Guidance:**\n\n"
            "Here is the fastest path from beginner to ML practitioner:\n"
            "1. **Python & Math Foundation**: Linear Algebra (matrices), Statistics (distributions, hypothesis tests), and NumPy/Pandas.\n"
            "2. **Scikit-Learn Mastery**: Linear/Logistic Regression, Decision Trees, Random Forests, and SVMs.\n"
            "3. **Hands-on Practice**: Complete the free [fast.ai](https://course.fast.ai) course and enter beginner competitions on [Kaggle](https://www.kaggle.com/learn).\n"
            "4. **Key Project Idea**: Build a predictive model deployed as an interactive FastAPI or Streamlit web app."
        )

    if any(k in msg for k in ["cyber", "security", "hack", "linux", "network"]):
        return (
            "🛡️ **Cybersecurity & Ethical Hacking Guidance:**\n\n"
            "Essential milestones for security analysts and penetration testers:\n"
            "1. **Networking Fundamentals**: Understand OSI Model, TCP/IP, DNS, Subnetting, and Firewalls.\n"
            "2. **Linux Command Line**: Master Bash scripting and permissions on [OverTheWire Bandit](https://overthewire.org).\n"
            "3. **Hands-on Labs**: Start with the free 'Pre-Security' path on [TryHackMe](https://tryhackme.com).\n"
            "4. **Target Certifications**: CompTIA Security+ or eJPT (Junior Penetration Tester)."
        )

    if any(k in msg for k in ["web", "react", "frontend", "fullstack", "node", "javascript"]):
        return (
            "🌐 **Full Stack Web Development Guidance:**\n\n"
            "1. **Frontend Mastery**: HTML5 Semantic markup, Modern CSS (Flexbox/Grid), and JavaScript (ES6+, DOM, Fetch API).\n"
            "2. **React Ecosystem**: Components, Props, State, Hooks (`useEffect`, `useState`), and React Router.\n"
            "3. **Backend & DB**: Node.js with Express, RESTful API architecture, and MongoDB or PostgreSQL.\n"
            "4. **Recommended Curriculum**: Complete [The Odin Project](https://www.theodinproject.com) and [freeCodeCamp](https://www.freecodecamp.org)."
        )

    if any(k in msg for k in ["internship", "job", "resume", "apply", "placement"]):
        return (
            "💼 **Internship & Placement Action Plan:**\n\n"
            "1. **Resume Structure**: Keep it strictly to 1 page. Use the STAR method (*Situation, Task, Action, Result*) for projects.\n"
            "2. **GitHub Profile**: Pin your top 3 polished projects with live demo URLs and clean README screenshots.\n"
            "3. **Target Student Programs**: Apply early to Google STEP, Microsoft Engage, Amazon SDE, and LinkedIn internships.\n"
            "4. **Cold Outreach**: Reach out to engineering recruiters and alumni on LinkedIn with a concise, personalized note."
        )

    if any(k in msg for k in ["dsa", "leetcode", "algorithm", "data structure"]):
        return (
            "⚡ **DSA & Coding Interview Strategy:**\n\n"
            "1. **Core Patterns**: Arrays, Two Pointers, Sliding Window, HashMaps, Binary Search, Trees, and Dynamic Programming basics.\n"
            "2. **Practice Target**: Solve the *NeetCode 150* or *Blind 75* questions on LeetCode.\n"
            "3. **Rule of Thumb**: Spend max 30 minutes struggling before checking hints, then write the code yourself from scratch without looking."
        )

    # General fallback
    return (
        f"💡 **AI Mentor Advice regarding: '{message}'**\n\n"
        "Here are 3 actionable steps to accelerate your tech journey:\n"
        "1. **Consistency beats intensity**: 1 hour of active coding or designing every single day builds compound mastery.\n"
        "2. **Build in Public**: Share your weekly learning milestones and projects on GitHub and LinkedIn.\n"
        "3. **Apply Your Roadmap**: Check your personalized milestones on the **My Roadmap** page and mark completed steps as you progress!"
    )


# ── Curated Intelligent Domain Study Tips Cache ──────────────────────────────
import random

DOMAIN_STUDY_TIPS = {
    "webdev": [
        "Master CSS Flexbox and Grid layouts thoroughly before jumping directly into CSS frameworks.",
        "Practice building small vanilla JavaScript apps (like a calculator or drag-and-drop board) to master DOM manipulation.",
        "Break your UI down into isolated, reusable React components and keep state localized where it is used.",
        "Always write clean REST API contracts with explicit status codes (200, 201, 400, 404, 500) for smooth frontend integration.",
        "Commit clean code with meaningful commit messages to GitHub daily to build a recruiter-ready portfolio.",
        "Always sanitize user inputs and use parameterized SQL queries or ORMs to prevent security vulnerabilities like SQL injection.",
        "Focus on building 3 polished full-stack applications with user authentication and database persistence rather than 10 unfinished toys.",
        "Learn browser DevTools performance profiling and network tab analysis to debug latency and render bottlenecks effortlessly."
    ],
    "aiml": [
        "Master NumPy array vectorization and broadcasting—it makes your machine learning pipelines 100x faster than Python loops.",
        "Spend 80% of your time exploring, cleaning, and visualizing your datasets with Pandas and Seaborn before training any model.",
        "Always evaluate ML models with cross-validation and confusion matrices instead of relying solely on baseline accuracy.",
        "Implement gradient descent and linear regression from scratch once with NumPy to build unshakeable mathematical intuition.",
        "Follow top-down practical learning with fast.ai and PyTorch to rapidly deploy real-world computer vision and NLP models.",
        "Participate in Kaggle beginner competitions and read top competitors' exploratory notebooks to learn production-grade feature engineering.",
        "Track your model hyperparameters and experiment metrics systematically using tools like MLflow or Weights & Biases.",
        "Deploy your trained AI models as interactive web apps using FastAPI and Streamlit to showcase tangible engineering capability."
    ],
    "cybersecurity": [
        "Deeply understand OSI layers and TCP/IP packet handshakes using Wireshark before diving into offensive security tools.",
        "Master Linux command line navigation, user permissions, and Bash automation scripting on OverTheWire Bandit challenges.",
        "Complete the beginner 'Pre-Security' and 'Complete Beginner' hands-on learning paths on TryHackMe to gain practical lab experience.",
        "Study the OWASP Top 10 vulnerabilities (SQLi, XSS, CSRF, IDOR) by testing purposely vulnerable environments like OWASP Juice Shop.",
        "Learn basic Python scripting to automate network scanning, reconnaissance, and log parsing tasks efficiently.",
        "Understand firewall rule configurations, symmetric/asymmetric encryption, and SSH key management for enterprise defense.",
        "Document your CTF challenge walkthroughs and writeups on a personal tech blog to impress security hiring managers."
    ],
    "datascience": [
        "SQL is essential for every data role—master window functions, GROUP BY, aggregations, and complex multi-table JOINs.",
        "Clean, well-labeled visualizations with Matplotlib and Seaborn communicate insights far more effectively than complex tables.",
        "Master core statistics: probability distributions, hypothesis testing (p-values, t-tests), and confidence intervals.",
        "Always formulate clear business questions before analyzing datasets to ensure your insights drive actionable decisions.",
        "Learn exploratory data analysis (EDA) techniques to detect anomalies, outliers, and missing data distributions reliably.",
        "Build interactive dashboards with Streamlit or Tableau to present data stories compellingly to non-technical stakeholders.",
        "Practice A/B test hypothesis formulation, sample sizing, and statistical significance analysis."
    ],
    "uiux": [
        "Adopt an 8pt spacing grid and strict typographic scale in Figma to create visually cohesive, balanced interfaces.",
        "Master Figma Auto Layout, constraints, and component variant properties to build flexible, developer-ready UI systems.",
        "Always test contrast ratios with WCAG 2.1 AA accessibility standards to ensure your designs are inclusive and readable.",
        "Conduct short usability tests with at least 3 real users on low-fidelity wireframes before polishing high-fidelity visuals.",
        "Design with edge cases in mind: empty states, loading skeletons, long text truncations, and error notifications.",
        "Structure your UX case studies around the problem, user research insights, design iterations, and measurable impact."
    ],
    "cloud": [
        "Master Docker multi-stage builds to create lightweight, secure production container images.",
        "Learn Infrastructure as Code (IaC) with Terraform to provision reproducible, version-controlled cloud infrastructure.",
        "Always enforce the principle of least privilege in cloud IAM roles and policies to prevent security breaches.",
        "Set up billing alerts and budget notifications on your AWS, GCP, or Azure account on day 1.",
        "Build automated CI/CD deployment pipelines using GitHub Actions to run tests and push code seamlessly.",
        "Use Minikube or Kind to experiment with Kubernetes pods, services, and ingress controllers locally without cloud costs."
    ],
    "mobile": [
        "Test your mobile apps on real physical devices early to catch platform-specific quirks, touch target issues, and frame drops.",
        "Always design responsive layouts that respect safe area insets on notched screens and dynamic status bars.",
        "Implement offline-first architecture with local SQLite or async caching so your app remains usable without internet connectivity.",
        "Follow platform design guidelines closely: Material Design for Android and Human Interface Guidelines for iOS.",
        "Prepare App Store and Play Store review assets, permissions descriptions, and privacy policies ahead of submission."
    ]
}


def generate_daily_study_tip(
    track_key: str = "webdev",
    milestone: Optional[str] = None,
    student_id: str = "user_001",
    custom_api_key: Optional[str] = None
) -> tuple[str, str]:
    """
    Generates a concise, 1-sentence personalized daily study tip via Google Gemini or intelligent domain cache.
    Returns (tip_text, source).
    """
    api_key = custom_api_key or settings.GEMINI_API_KEY or ""
    clean_track = (track_key or "webdev").lower().strip()
    
    # Normalize track aliases
    if clean_track in ("web", "fullstack", "web-development"):
        clean_track = "webdev"
    elif clean_track in ("ai", "ml", "ai-ml", "machine-learning"):
        clean_track = "aiml"
    elif clean_track in ("security", "cyber", "infosec"):
        clean_track = "cybersecurity"
    elif clean_track in ("data", "analytics", "ds"):
        clean_track = "datascience"
    elif clean_track in ("design", "ux", "ui"):
        clean_track = "uiux"
    elif clean_track in ("devops", "aws"):
        clean_track = "cloud"
    elif clean_track in ("app", "android", "ios"):
        clean_track = "mobile"

    topic_context = f"{clean_track.upper()} engineering"
    if milestone:
        topic_context += f" (focusing on {milestone})"

    # 1. Try Gemini 1.5 Flash
    if api_key and not api_key.startswith("gsk_") and not api_key.startswith("xai-"):
        try:
            prompt = (
                f"You are a supportive, expert tech mentor. Provide exactly ONE punchy, actionable, highly practical 1-sentence study or career tip "
                f"for a computer science student learning {topic_context}. "
                f"Requirements: Strictly 1 concise sentence, no quotation marks, no preamble, actionable and inspiring."
            )
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.8, "maxOutputTokens": 80}
            }
            res = requests.post(url, headers=headers, json=payload, timeout=8)
            if res.ok:
                data = res.json()
                tip_candidate = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                if tip_candidate:
                    # Clean any surrounding quotes or markdown
                    tip_candidate = tip_candidate.strip('"\n*`\' ')
                    if len(tip_candidate) > 15:
                        return tip_candidate, "gemini"
        except Exception as e:
            logger.warning(f"Gemini daily tip generation fallback triggered: {e}")

    # 2. Intelligent Domain-Aware Built-in Study Tip Cache (Fallback)
    pool = DOMAIN_STUDY_TIPS.get(clean_track, DOMAIN_STUDY_TIPS["webdev"])
    selected_tip = random.choice(pool)
    return selected_tip, "domain_cache"

