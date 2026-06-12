import pandas as pd
import logging
from models.recommendation_model import recommender

logger = logging.getLogger(__name__)

CSV_PATH = "data/general_mcqs.csv"


def get_general_questions():
    """
    Loads general questions from the CSV file and returns them in a list format
    suitable for the frontend (excluding Correct_Answer and Category).
    """
    try:
        df = pd.read_csv(CSV_PATH)
        questions = []
        for index, row in df.iterrows():
            questions.append({
                "id": f"q{index + 1}",
                "question": row["Question"],
                "options": {
                    "A": row["Option_A"],
                    "B": row["Option_B"],
                    "C": row["Option_C"],
                    "D": row["Option_D"]
                }
            })
        return questions
    except Exception as e:
        logger.error(f"Error loading general questions: {e}")
        return []


def evaluate_general_quiz(student_id: str, answers: dict) -> dict:
    """
    Evaluates student's answers for the general quiz.
    Computes scores for each of the 6 domain features and calls the career recommender.
    """
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        logger.error(f"Error reading general quiz CSV: {e}")
        raise ValueError("General quiz questions data not available.")

    categories = [
        "programming_score", "logical_score", "networking_score",
        "ai_score", "cyber_score", "communication_score"
    ]

    correct_counts = {cat: 0 for cat in categories}
    total_counts = {cat: 0 for cat in categories}
    total_correct = 0

    # Grade each answer
    for index, row in df.iterrows():
        q_id = f"q{index + 1}"
        category = row["Category"]

        if category in total_counts:
            total_counts[category] += 1

        student_answer = answers.get(q_id)
        if student_answer:
            correct_answer = str(row["Correct_Answer"]).strip().upper()
            if student_answer.strip().upper() == correct_answer:
                total_correct += 1
                if category in correct_counts:
                    correct_counts[category] += 1

    # Calculate percentage scores
    scores = {}
    for cat in categories:
        if cat == "ai_score":
            continue  # Computed below
        total = total_counts.get(cat, 0)
        correct = correct_counts.get(cat, 0)
        scores[cat] = round((correct / total) * 100.0, 2) if total > 0 else 0.0

    # Calculate ai_score as average of programming_score and logical_score
    scores["ai_score"] = round((scores["programming_score"] + scores["logical_score"]) / 2.0, 2)

    # Determine level
    if total_correct <= 10:
        level_label = "Beginner"
        level_key = "beginner"
        level_desc = "You are just starting your computing journey. Let's focus on basic hardware, simple logic, and everyday digital tools."
    elif total_correct <= 20:
        level_label = "Foundation"
        level_key = "foundation"
        level_desc = "You have basic digital literacy but need to strengthen your file/OS management and web fundamentals before moving to advanced topics."
    else:
        level_label = "Ready for CS"
        level_key = "ready"
        level_desc = "Excellent! You have a solid grasp of basic computer concepts and are ready to jump into programming and Computer Science."

    # Map internal score key to friendly topic descriptions and resources
    recommendations_map = {
        "logical_score": {
            "title": "Computer Basics & Logic",
            "beginner": {
                "desc": "Understand computer components like CPU, RAM, storage, and how inputs/outputs are processed.",
                "action": "We recommend learning how hardware fits together.",
                "materials": [
                    {"label": "GCFGlobal: Computer Basics Tutorial", "url": "https://edu.gcfglobal.org/en/computerbasics/"},
                    {"label": "Code.org: How Computers Work Video Series", "url": "https://www.youtube.com/playlist?list=PLzdnOPI1iJNfMRZm5DDxco3UdsFegvuB7"}
                ]
            },
            "foundation": {
                "desc": "Learn how basic logic gates work, binary numbering systems, and computational problem solving.",
                "action": "Focus on logic fundamentals and numerical operations.",
                "materials": [
                    {"label": "GeeksforGeeks: Logic Gates Explained", "url": "https://www.geeksforgeeks.org/logic-gates-in-detail/"},
                    {"label": "Khan Academy: Binary Number System", "url": "https://www.khanacademy.org/computing/ap-computer-science-principles/ap-data-representation-principles/x2d8a7ecd35a5ef1d:binary-numbers/a/binary-numbers"}
                ]
            }
        },
        "programming_score": {
            "title": "Operating Systems & File Structures",
            "beginner": {
                "desc": "Learn how operating systems manage programs, run files, and structure directories.",
                "action": "Practice organizing files, understanding paths, and common extensions.",
                "materials": [
                    {"label": "GCFGlobal: Working with Files & Paths", "url": "https://edu.gcfglobal.org/en/computerbasics/working-with-files/1/"},
                    {"label": "GCFGlobal: Understanding Operating Systems", "url": "https://edu.gcfglobal.org/en/computerbasics/understanding-operating-systems/1/"}
                ]
            },
            "foundation": {
                "desc": "Understand command-line terminal concepts, basic execution environments, and scripting paths.",
                "action": "Learn basic commands in Windows PowerShell or Linux terminal.",
                "materials": [
                    {"label": "W3Schools: Command Line Intro", "url": "https://www.w3schools.com/codeline/index.php"},
                    {"label": "freeCodeCamp: Linux Command Line Course", "url": "https://www.freecodecamp.org/news/linux-command-line-tutorial-for-beginners/"}
                ]
            }
        },
        "networking_score": {
            "title": "Internet Fundamentals",
            "beginner": {
                "desc": "Learn about the World Wide Web, web browsers, and basic web navigation.",
                "action": "Read about web search engines and browser structures.",
                "materials": [
                    {"label": "GCFGlobal: Web Browsers and Search Essentials", "url": "https://edu.gcfglobal.org/en/internetbasics/what-is-a-web-browser/1/"},
                    {"label": "Google Help: Web Search Tips", "url": "https://support.google.com/websearch/answer/134479?hl=en"}
                ]
            },
            "foundation": {
                "desc": "Understand how web client-server requests work, IP addresses, HTTP vs HTTPS protocol, and DNS.",
                "action": "Learn how the internet communicates requests and routes data.",
                "materials": [
                    {"label": "MDN Web Docs: How the Web Works", "url": "https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/How_the_Web_works"},
                    {"label": "Cloudflare: What is DNS & IP?", "url": "https://www.cloudflare.com/learning/dns/what-is-dns/"}
                ]
            }
        },
        "cyber_score": {
            "title": "Digital Safety & Security",
            "beginner": {
                "desc": "Master basic password security, account protections, and identifying suspicious files/emails.",
                "action": "Review password complexity guidelines and security hygiene.",
                "materials": [
                    {"label": "GCFGlobal: Safe Password Habits", "url": "https://edu.gcfglobal.org/en/internetsafety/creating-strong-passwords/1/"},
                    {"label": "Google Safety Center: Security Basics", "url": "https://safety.google/security-basics/"}
                ]
            },
            "foundation": {
                "desc": "Learn about phishing detection models, multi-factor authentication (MFA), and encryption concepts.",
                "action": "Learn to detect online scams and secure software platforms.",
                "materials": [
                    {"label": "Google Jigsaw: Phishing Detection Test", "url": "https://phishingquiz.withgoogle.com/"},
                    {"label": "CISA: Multi-Factor Authentication Guide", "url": "https://www.cisa.gov/resources-tools/resources/multi-factor-authentication-mfa"}
                ]
            }
        },
        "communication_score": {
            "title": "Digital Tools & Communication",
            "beginner": {
                "desc": "Learn to write formal emails, compose documents, and structure presentations.",
                "action": "Practice drafting simple letters in MS Word and formatting slides.",
                "materials": [
                    {"label": "GCFGlobal: Email Basics Course", "url": "https://edu.gcfglobal.org/en/email101/introduction-to-email/1/"},
                    {"label": "GCFGlobal: Word for Beginners", "url": "https://edu.gcfglobal.org/en/word/"}
                ]
            },
            "foundation": {
                "desc": "Learn collaborative sharing models, markdown formatting, and digital version control concepts.",
                "action": "Practice using Markdown syntax and editing shared cloud documents.",
                "materials": [
                    {"label": "Markdown Guide: Basic Syntax Tutorials", "url": "https://www.markdownguide.org/basic-syntax/"},
                    {"label": "Google Docs Workspace: Collaborative Editing", "url": "https://support.google.com/a/users/answer/9300322?hl=en"}
                ]
            }
        }
    }

    weak_topics = []
    # If beginner or foundation, select the appropriate sub-dictionary
    if level_key in ["beginner", "foundation"]:
        for cat, rec in recommendations_map.items():
            if scores.get(cat, 0) < 70.0:
                weak_topics.append({
                    "title": rec["title"],
                    "data": rec[level_key]
                })

    learning_path = f"<strong>Current Level: {level_label}</strong><br/>"
    learning_path += f"<span style='color: var(--text-muted); font-size: 0.95rem;'>{level_desc}</span><br/><br/>"

    if level_key in ["beginner", "foundation"] and weak_topics:
        learning_path += "<strong>🎯 Recommended Focus Areas & Study Materials:</strong><br/>"
        learning_path += "<ul style='margin-left: 20px; margin-top: 8px; display: flex; flex-direction: column; gap: 14px; list-style-type: disc;'>"
        for topic in weak_topics:
            t_data = topic["data"]
            materials_html = ", ".join([
                f"<a href='{mat['url']}' target='_blank' style='color: var(--blue); text-decoration: underline;'>{mat['label']}</a>"
                for mat in t_data["materials"]
            ])
            learning_path += (
                f"<li style='margin-bottom: 6px; line-height: 1.5;'>"
                f"<strong>{topic['title']}</strong>: {t_data['desc']}<br/>"
                f"<em style='font-size: 0.85rem;'>Suggested: {t_data['action']}</em><br/>"
                f"<span style='font-size: 0.85rem; color: var(--text-muted);'>📚 Study Material: {materials_html}</span>"
                f"</li>"
            )
        learning_path += "</ul>"
    elif level_key in ["beginner", "foundation"]:
        learning_path += "<strong>🎯 Recommended Focus Areas & Study Materials:</strong><br/>"
        learning_path += (
            "<ul style='margin-left: 20px; margin-top: 8px; display: flex; flex-direction: column; gap: 8px; list-style-type: disc;'>"
            "<li style='line-height: 1.5;'>"
            "<strong>Foundational CS Literacy</strong>: You scored well across all general categories! You are ready to start exploring basic coding concepts.<br/>"
            "<span style='font-size: 0.85rem; color: var(--text-muted);'>📚 Study Material: "
            "<a href='https://scratch.mit.edu/' target='_blank' style='color: var(--blue); text-decoration: underline;'>Scratch (Intro to Programming)</a>, "
            "<a href='https://www.w3schools.com/python/' target='_blank' style='color: var(--blue); text-decoration: underline;'>W3Schools: Python Tutorial</a>"
            "</span>"
            "</li>"
            "</ul>"
        )
    else:
        # Ready for CS
        learning_path += "<strong>🎯 Recommended Focus Areas & Study Materials:</strong><br/>"
        learning_path += (
            "<ul style='margin-left: 20px; margin-top: 8px; display: flex; flex-direction: column; gap: 8px; list-style-type: disc;'>"
            "<li style='line-height: 1.5;'>"
            "<strong>Ready for Computer Science!</strong>: You have a solid grasp of basic computer concepts and are fully prepared to start CS learning.<br/>"
            "<span style='font-size: 0.85rem; color: var(--text-muted);'>📚 Study Material: "
            "<a href='https://www.w3schools.com/python/' target='_blank' style='color: var(--blue); text-decoration: underline;'>W3Schools: Python Programming</a>, "
            "<a href='https://www.freecodecamp.org/learn/responsive-web-design/' target='_blank' style='color: var(--blue); text-decoration: underline;'>freeCodeCamp: HTML/CSS Basics</a>, "
            "<a href='https://www.geeksforgeeks.org/data-structures/' target='_blank' style='color: var(--blue); text-decoration: underline;'>GeeksforGeeks: Intro to Data Structures</a>"
            "</span>"
            "</li>"
            "</ul>"
        )

    can_proceed = total_correct >= 21

    return {
        "student_id": student_id,
        "total_correct": total_correct,
        "recommended_learning_path": learning_path,
        "can_proceed_to_cs_quiz": can_proceed,
        "scores": scores,
        "recommendations": []
    }
