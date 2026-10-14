import logging
import requests
from typing import Optional, Dict, Any, List
from config import settings

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are an expert AI Career & Technical Mentor for engineering and computer science students.
Your mission is to provide clear, actionable, friendly, and structured guidance on:
- Learning roadmaps (UI/UX Design, AI/ML, Cybersecurity, Web Development, Data Science, Cloud/DevOps, Mobile App Dev)
- Technical explanations with clean code examples
- Resume, interview preparation, internship strategies, and portfolio building
- Step-by-step problem-solving approaches.

Format your responses with clear markdown, bullet points, and actionable next steps."""

# ── Dynamic Track Roadmap Metadata & Tailored Practice Challenges ───────────
TRACK_ROADMAP_METADATA = {
    "webdev": {
        "title": "Full-Stack Web Engineering",
        "milestones": [
            {
                "index": 0,
                "title": "HTML5 & CSS Responsive Grid",
                "week": "Week 1 – 2",
                "topics": ["Semantic HTML", "CSS Flexbox & Grid", "Media Queries", "Responsive Layouts"],
                "challenge": "Implement a viewport breakpoint analyzer that maps screen pixel widths to responsive grid column configurations.",
                "lang": "javascript",
                "starterCode": """// Milestone 1 Challenge: Responsive Grid Breakpoint Helper
function getActiveBreakpoint(viewportWidth) {
    if (viewportWidth >= 1200) return { breakpoint: "xl", columns: 12, label: "Desktop Wide" };
    if (viewportWidth >= 992)  return { breakpoint: "lg", columns: 8,  label: "Laptop" };
    if (viewportWidth >= 768)  return { breakpoint: "md", columns: 6,  label: "Tablet" };
    return { breakpoint: "sm", columns: 2, label: "Mobile" };
}

console.log("Viewport 1440px ->", getActiveBreakpoint(1440));
console.log("Viewport 820px  ->", getActiveBreakpoint(820));
console.log("Viewport 390px  ->", getActiveBreakpoint(390));"""
            },
            {
                "index": 1,
                "title": "JavaScript Fundamentals & DOM",
                "week": "Week 3 – 4",
                "topics": ["Variables & scoping", "Higher-order array methods", "Async/await & Promises", "DOM event listeners"],
                "challenge": "Build an async task filtering function using map, filter, and reduce to calculate study completion metrics.",
                "lang": "javascript",
                "starterCode": """// Milestone 2 Challenge: Array Transformation & Statistics
const learningTasks = [
    { title: "Flexbox Froggy", completed: true, timeMinutes: 30 },
    { title: "DOM Event Delegation", completed: true, timeMinutes: 45 },
    { title: "Fetch API & JSON", completed: false, timeMinutes: 60 },
    { title: "Async/Await Refactoring", completed: false, timeMinutes: 40 }
];

function analyzeRoadmapTasks(tasks) {
    const completed = tasks.filter(t => t.completed);
    const totalTimeSpent = completed.reduce((sum, t) => sum + t.timeMinutes, 0);
    const pendingNames = tasks.filter(t => !t.completed).map(t => t.title);

    return {
        completedCount: completed.length,
        totalTimeSpentMinutes: totalTimeSpent,
        nextUpcoming: pendingNames[0] || "None"
    };
}

console.log("Task Progress Report:", analyzeRoadmapTasks(learningTasks));"""
            },
            {
                "index": 2,
                "title": "React.js State & Hooks",
                "week": "Week 5 – 6",
                "topics": ["Functional components", "useState & useEffect", "Component props", "Custom hooks"],
                "challenge": "Implement a pure state reducer simulation for managing a counter and study log history.",
                "lang": "javascript",
                "starterCode": """// Milestone 3 Challenge: Reducer State Simulation
function studyLogReducer(state, action) {
    switch (action.type) {
        case 'LOG_HOURS':
            return {
                ...state,
                totalHours: state.totalHours + action.hours,
                logs: [...state.logs, { day: action.day, hours: action.hours }]
            };
        case 'RESET':
            return { totalHours: 0, logs: [] };
        default:
            return state;
    }
}

let state = { totalHours: 0, logs: [] };
state = studyLogReducer(state, { type: 'LOG_HOURS', day: 'Mon', hours: 2.5 });
state = studyLogReducer(state, { type: 'LOG_HOURS', day: 'Tue', hours: 3.0 });
console.log("Final State:", state);"""
            },
            {
                "index": 3,
                "title": "Backend APIs with Node.js & Express",
                "week": "Week 7 – 8",
                "topics": ["Express route controllers", "Middleware chaining", "REST status codes", "Input validation"],
                "challenge": "Write a mock Express route validation middleware function.",
                "lang": "python",
                "starterCode": """# Milestone 4 Challenge: API Request Validator
def validate_student_payload(data):
    required_fields = ["student_id", "track_key", "milestone_index"]
    missing = [f for f in required_fields if f not in data or data[f] is None]
    
    if missing:
        return {"valid": False, "status": 400, "error": f"Missing required fields: {', '.join(missing)}"}
    
    if not isinstance(data["milestone_index"], int) or data["milestone_index"] < 0:
        return {"valid": False, "status": 422, "error": "milestone_index must be a non-negative integer"}
    
    return {"valid": True, "status": 200, "message": "Payload verified."}

print(validate_student_payload({"student_id": "user_001", "track_key": "webdev", "milestone_index": 2}))
print(validate_student_payload({"student_id": "user_001", "milestone_index": -1}))"""
            },
            {
                "index": 4,
                "title": "Database Schema Design & Full Stack Project",
                "week": "Week 9 – 12",
                "topics": ["Relational DB schemas", "SQL queries & indexing", "JWT authentication", "Cloud deployment"],
                "challenge": "Write an in-memory SQL mock query to aggregate student scores.",
                "lang": "python",
                "starterCode": """# Milestone 5 Challenge: Leaderboard Aggregator
students = [
    {"name": "Astha", "score": 98, "track": "webdev"},
    {"name": "Rahul", "score": 85, "track": "aiml"},
    {"name": "Priya", "score": 94, "track": "webdev"},
    {"name": "Karan", "score": 79, "track": "webdev"}
]

def rank_students_by_track(records, track):
    filtered = [s for s in records if s["track"] == track]
    sorted_records = sorted(filtered, key=lambda x: x["score"], reverse=True)
    return [{"rank": i + 1, "name": s["name"], "score": s["score"]} for i, s in enumerate(sorted_records)]

print("WebDev Rankings:", rank_students_by_track(students, "webdev"))"""
            }
        ]
    },
    "aiml": {
        "title": "AI & Machine Learning Engineering",
        "milestones": [
            {
                "index": 0,
                "title": "Python for Data Science & NumPy",
                "week": "Week 1 – 2",
                "topics": ["NumPy array broadcasting", "Pandas DataFrame operations", "Vectorized math", "Matplotlib"],
                "challenge": "Implement vector Euclidean distance and Cosine Similarity without heavy dependencies.",
                "lang": "python",
                "starterCode": """# Milestone 1 Challenge: Vector Operations from Scratch
import math

def euclidean_distance(v1, v2):
    if len(v1) != len(v2):
        raise ValueError("Vectors must have equal length")
    return round(math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2))), 4)

def cosine_similarity(v1, v2):
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a ** 2 for a in v1))
    norm_v2 = math.sqrt(sum(b ** 2 for b in v2))
    return round(dot_product / (norm_v1 * norm_v2), 4)

vec_a = [1.2, 3.4, 0.8]
vec_b = [1.5, 3.1, 1.0]

print("Euclidean Distance:", euclidean_distance(vec_a, vec_b))
print("Cosine Similarity: ", cosine_similarity(vec_a, vec_b))"""
            },
            {
                "index": 1,
                "title": "Supervised Learning & Model Evaluation",
                "week": "Week 3 – 4",
                "topics": ["Linear & Logistic Regression", "Decision Trees", "Train-Test Splits", "Confusion Matrix & F1-Score"],
                "challenge": "Calculate Precision, Recall, Accuracy, and F1-score from raw confusion matrix values.",
                "lang": "python",
                "starterCode": """# Milestone 2 Challenge: Classification Metrics Evaluator
def evaluate_classification(tp, fp, tn, fn):
    accuracy = (tp + tn) / (tp + fp + tn + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "Accuracy": round(accuracy, 4),
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1_Score": round(f1, 4)
    }

print("Model Performance:", evaluate_classification(tp=85, fp=15, tn=90, fn=10))"""
            },
            {
                "index": 2,
                "title": "Deep Learning & Neural Networks",
                "week": "Week 5 – 6",
                "topics": ["Multilayer Perceptrons", "Activation functions (ReLU, Sigmoid)", "Backpropagation", "PyTorch tensors"],
                "challenge": "Implement forward pass of a 2-layer neural network with ReLU activation.",
                "lang": "python",
                "starterCode": """# Milestone 3 Challenge: 2-Layer Forward Pass with ReLU
def relu(x):
    return max(0.0, x)

def forward_pass(inputs, weights, bias):
    z = sum(w * x for w, x in zip(weights, inputs)) + bias
    return relu(z)

x = [0.5, 1.2]
w = [0.4, -0.2]
b = 0.1

output = forward_pass(x, w, b)
print("Input:", x)
print("Neuron Output (ReLU):", round(output, 4))"""
            }
        ]
    },
    "cybersecurity": {
        "title": "Cybersecurity & Defense Analysis",
        "milestones": [
            {
                "index": 0,
                "title": "Networking & Linux Security Foundations",
                "week": "Week 1 – 2",
                "topics": ["OSI model & TCP/IP handshakes", "Linux permission bitmasks", "Bash scripting", "Wireshark packet analysis"],
                "challenge": "Parse CIDR notation to calculate subnet host capacity.",
                "lang": "python",
                "starterCode": """# Milestone 1 Challenge: Subnet Capacity Calculator
def cidr_hosts(cidr_mask):
    if not (0 <= cidr_mask <= 32):
        raise ValueError("Invalid CIDR mask")
    host_bits = 32 - cidr_mask
    total_addresses = 2 ** host_bits
    usable_hosts = max(0, total_addresses - 2)
    return {"mask": f"/{cidr_mask}", "totalAddresses": total_addresses, "usableHosts": usable_hosts}

for mask in [24, 28, 30]:
    print(f"Mask /{mask}:", cidr_hosts(mask))"""
            },
            {
                "index": 1,
                "title": "Web Security & OWASP Top 10 Defense",
                "week": "Week 3 – 4",
                "topics": ["SQL Injection sanitization", "XSS mitigation & CSP", "CSRF tokens", "IDOR prevention"],
                "challenge": "Write an HTML sanitizer function to escape dangerous tags.",
                "lang": "python",
                "starterCode": """# Milestone 2 Challenge: XSS HTML Sanitizer
import html

def sanitize_user_comment(comment):
    sanitized = html.escape(comment.strip())
    has_script_payload = any(tag in comment.lower() for tag in ["<script>", "javascript:", "onload=", "onerror="])
    return {
        "originalLength": len(comment),
        "sanitizedOutput": sanitized,
        "threatFlagged": has_script_payload
    }

print(sanitize_user_comment("Hello World! Great article."))
print(sanitize_user_comment("<script>alert('XSS')</script>"))"""
            }
        ]
    },
    "datascience": {
        "title": "Data Science & Analytics",
        "milestones": [
            {
                "index": 0,
                "title": "Data Wrangling & Statistical Foundations",
                "week": "Week 1 – 2",
                "topics": ["Pandas aggregation", "Mean, Median, Standard Deviation", "Outlier detection (IQR)", "Data cleaning"],
                "challenge": "Detect outliers using IQR rule.",
                "lang": "python",
                "starterCode": """# Milestone 1 Challenge: IQR Outlier Detector
def find_iqr_outliers(data):
    sorted_d = sorted(data)
    n = len(sorted_d)
    q1 = sorted_d[n // 4]
    q3 = sorted_d[(3 * n) // 4]
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    outliers = [x for x in data if x < lower_bound or x > upper_bound]
    return {"Q1": q1, "Q3": q3, "IQR": iqr, "outliers": outliers}

salaries = [35000, 42000, 45000, 49000, 52000, 55000, 58000, 62000, 150000]
print("Outlier Detection:", find_iqr_outliers(salaries))"""
            }
        ]
    },
    "uiux": {
        "title": "UI/UX & Product Design",
        "milestones": [
            {
                "index": 0,
                "title": "Design Systems & 8pt Grid Layouts",
                "week": "Week 1 – 2",
                "topics": ["8pt grid alignment", "WCAG AA contrast calculation", "Auto Layout", "Component tokens"],
                "challenge": "Calculate if a color contrast ratio satisfies WCAG AA (4.5:1).",
                "lang": "javascript",
                "starterCode": """// Milestone 1 Challenge: WCAG Contrast Ratio Checker
function calculateRelativeLuminance(r, g, b) {
    const sRGB = [r, g, b].map(v => {
        v /= 255;
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * sRGB[0] + 0.7152 * sRGB[1] + 0.0722 * sRGB[2];
}

function checkContrast(lum1, lum2) {
    const brighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    const ratio = (brighter + 0.05) / (darker + 0.05);
    return {
        ratio: ratio.toFixed(2) + ":1",
        passesAA: ratio >= 4.5
    };
}

const textLum = calculateRelativeLuminance(15, 23, 42); // Slate 900
const bgLum = calculateRelativeLuminance(255, 255, 255); // White
console.log("Contrast Result:", checkContrast(textLum, bgLum));"""
            }
        ]
    },
    "cloud": {
        "title": "Cloud Architecture & DevOps",
        "milestones": [
            {
                "index": 0,
                "title": "Docker Containers & Microservices",
                "week": "Week 1 – 2",
                "topics": ["Multi-stage Dockerfiles", "Image optimization", "Container networks", "Docker Compose"],
                "challenge": "Parse and validate environment variables for container configuration.",
                "lang": "python",
                "starterCode": """# Milestone 1 Challenge: Container Env Validator
def validate_container_env(env_vars):
    required = ["PORT", "DATABASE_URL", "NODE_ENV"]
    missing = [k for k in required if k not in env_vars]
    port_valid = str(env_vars.get("PORT", "")).isdigit()
    
    return {
        "isValid": len(missing) == 0 and port_valid,
        "missing": missing,
        "portValid": port_valid
    }

print("Dev Config:", validate_container_env({"PORT": "8000", "DATABASE_URL": "sqlite:///db.sqlite", "NODE_ENV": "development"}))
print("Broken Config:", validate_container_env({"PORT": "abc"}))"""
            }
        ]
    }
}


def get_student_roadmap_context(student_id: str, track_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieves the student's active roadmap milestone progress, completion metrics,
    and tailored practice problems to enable context-aware AI mentorship.
    """
    from services.auth_service import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    active_track = (track_key or "").lower().strip()
    student_name = "Student"

    # Lookup user info
    try:
        cursor.execute("SELECT full_name, career_track FROM users WHERE id = ? OR email = ?", (student_id, student_id))
        user_row = cursor.fetchone()
        if user_row:
            student_name = user_row["full_name"] or "Student"
            if not active_track and user_row["career_track"]:
                active_track = user_row["career_track"].lower().strip()
    except Exception:
        pass

    # If track still not known, check roadmap_subtasks
    if not active_track or active_track not in TRACK_ROADMAP_METADATA:
        try:
            cursor.execute("SELECT track_key FROM roadmap_subtasks WHERE student_id = ? ORDER BY completed_at DESC LIMIT 1", (student_id,))
            st_row = cursor.fetchone()
            if st_row and st_row["track_key"]:
                active_track = st_row["track_key"].lower().strip()
        except Exception:
            pass

    # Normalize track aliases
    if active_track in ("cyber", "infosec", "security"):
        active_track = "cybersecurity"
    elif active_track in ("web", "fullstack", "frontend"):
        active_track = "webdev"
    elif active_track in ("ai", "ml", "machine-learning"):
        active_track = "aiml"
    elif active_track in ("ds", "data", "analytics"):
        active_track = "datascience"
    elif active_track in ("design", "ux", "ui"):
        active_track = "uiux"
    elif active_track in ("devops", "aws", "gcp"):
        active_track = "cloud"

    if active_track not in TRACK_ROADMAP_METADATA:
        active_track = "webdev"

    track_info = TRACK_ROADMAP_METADATA[active_track]
    track_title = track_info["title"]
    milestones = track_info["milestones"]

    # Query subtasks
    subtasks = []
    try:
        cursor.execute("""
        SELECT subtask_id, is_completed, milestone_index, subtask_text
        FROM roadmap_subtasks
        WHERE student_id = ? AND (track_key = ? OR track_key = ?)
        """, (student_id, active_track, "webdev" if active_track == "webdev" else active_track))
        subtasks = cursor.fetchall()
    except Exception:
        pass

    conn.close()

    total_subtasks = len(subtasks)
    completed_subtasks = sum(1 for s in subtasks if s["is_completed"])
    percent_complete = round((completed_subtasks / total_subtasks * 100), 1) if total_subtasks > 0 else 25.0

    # Determine current active milestone (earliest with incomplete subtasks)
    incomplete_indices = [s["milestone_index"] for s in subtasks if not s["is_completed"] and s["milestone_index"] is not None]
    if incomplete_indices:
        current_idx = min(incomplete_indices)
    elif completed_subtasks == total_subtasks and total_subtasks > 0:
        current_idx = min(len(milestones) - 1, completed_subtasks // 2)
    else:
        current_idx = 1 if len(milestones) > 1 else 0

    if current_idx >= len(milestones):
        current_idx = len(milestones) - 1

    current_milestone = milestones[current_idx]
    pending_topics = current_milestone.get("topics", [])
    starter_code = current_milestone.get("starterCode", "")
    challenge_desc = current_milestone.get("challenge", "Complete the coding challenge for this stage.")
    lang = current_milestone.get("lang", "python")

    return {
        "studentId": student_id,
        "studentName": student_name,
        "trackKey": active_track,
        "trackTitle": track_title,
        "milestoneIndex": current_idx,
        "milestoneNumber": current_idx + 1,
        "milestoneTitle": current_milestone["title"],
        "milestoneWeek": current_milestone.get("week", f"Stage {current_idx + 1}"),
        "percentComplete": percent_complete,
        "completedSubtasks": completed_subtasks,
        "totalSubtasks": total_subtasks,
        "pendingTopics": pending_topics,
        "practiceProblem": {
            "title": f"Practice Challenge: {current_milestone['title']}",
            "description": challenge_desc,
            "language": lang,
            "starterCode": starter_code
        },
        "suggestedPracticePrompt": f"I'm currently working on Milestone {current_idx + 1}: {current_milestone['title']} in my {track_title} roadmap. Give me a practice coding problem to test my skills on {', '.join(pending_topics[:2])}!",
        "suggestedExplanationPrompt": f"Can you explain the core concepts of Milestone {current_idx + 1}: {current_milestone['title']} with practical examples?"
    }


def mentor_chat(student_id: str, message: str, custom_api_key: Optional[str] = None) -> str:
    """
    Generates a personalized AI Mentor response using Google Gemini, Groq, or an intelligent fallback expert system.
    """
    api_key = custom_api_key or settings.GEMINI_API_KEY or ""

    # Fetch live student context & roadmap memory from SQLite
    context_addon = ""
    roadmap_ctx = None
    try:
        roadmap_ctx = get_student_roadmap_context(student_id)
        if roadmap_ctx:
            context_addon += (
                f"\n\nStudent Learning Roadmap Status: Enrolled in '{roadmap_ctx['trackTitle']}' ({roadmap_ctx['trackKey']}), "
                f"currently on Milestone {roadmap_ctx['milestoneNumber']}: '{roadmap_ctx['milestoneTitle']}' "
                f"({roadmap_ctx['percentComplete']}% overall progress). Pending topics: {', '.join(roadmap_ctx['pendingTopics'][:3])}. "
                f"When the student asks what to practice, asks for coding exercises, or asks for roadmap help, "
                f"provide a tailored, runnable code problem for this milestone."
            )
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
                    {"role": "system", "content": full_system_instruction},
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
    return generate_intelligent_mentor_response(message, roadmap_ctx=roadmap_ctx)


def generate_intelligent_mentor_response(message: str, roadmap_ctx: Optional[Dict[str, Any]] = None) -> str:
    """
    Intelligent dynamic response generator when external API keys are unreachable.
    Provides structured, domain-specific mentorship for students.
    """
    msg = (message or "").lower()

    # Context-Aware Roadmap Milestone Practice & Assistance
    if roadmap_ctx and any(k in msg for k in ["practice", "problem", "challenge", "exercise", "code", "stuck", "what next", "milestone", "current step"]):
        prob = roadmap_ctx["practiceProblem"]
        lang = prob.get("language", "python")
        topics_str = ", ".join(roadmap_ctx["pendingTopics"])
        return (
            f"🎯 **Tailored Roadmap Practice: Milestone {roadmap_ctx['milestoneNumber']} — {roadmap_ctx['milestoneTitle']}**\n\n"
            f"You are currently progressing through the **{roadmap_ctx['trackTitle']}** track ({roadmap_ctx['percentComplete']}% complete).\n\n"
            f"**Focus Topics:** {topics_str}\n\n"
            f"### Challenge Description:\n"
            f"{prob['description']}\n\n"
            f"```{lang}\n"
            f"{prob['starterCode']}\n"
            f"```\n\n"
            f"💡 **Interactive Sandbox:** Click **▶ Run Code** in the sandbox directly below this message to execute this solution. You can also edit values inside the code block before running to test custom test cases!"
        )

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

