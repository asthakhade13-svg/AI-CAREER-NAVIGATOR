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
    Generates an AI Mentor response using Google Gemini, Groq, or an intelligent fallback expert system.
    """
    api_key = custom_api_key or settings.GEMINI_API_KEY or ""

    # 1. Try Google Gemini REST API (v1beta gemini-1.5-flash)
    if api_key and not api_key.startswith("gsk_") and not api_key.startswith("xai-"):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "systemInstruction": {
                    "parts": [{"text": SYSTEM_INSTRUCTION}]
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
