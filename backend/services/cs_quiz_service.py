import pandas as pd
import logging
from models.recommendation_model import recommender

logger = logging.getLogger(__name__)

CSV_PATH = "data/cs_mcqs.csv"

# Category-to-domain mapping
CATEGORY_MAP = {
    # programming_score
    "Programming Fundamentals": "programming_score",
    "Web Technologies": "programming_score",

    # logical_score
    "Data Structures & Algorithms": "logical_score",
    "Operating Systems": "logical_score",
    "Databases (SQL/NoSQL)": "logical_score",
    "Number Systems": "logical_score",

    # networking_score
    "Computer Networks": "networking_score",
    "Cloud Computing": "networking_score",

    # ai_score
    "Artificial Intelligence": "ai_score",

    # cyber_score
    "Cyber Security": "cyber_score",

    # communication_score (mapped via collaborative version control)
    "Git & Version Control": "communication_score"
}


def get_cs_questions():
    """
    Loads CS quiz questions from the CSV file and returns them in a list format
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
        logger.error(f"Error loading CS questions: {e}")
        return []


def evaluate_cs_quiz(student_id: str, answers: dict) -> dict:
    """
    Evaluates student's answers for the CS quiz.
    Computes scores for each of the 6 domain features using the CATEGORY_MAP,
    then calls the career recommender to predict top career paths.
    """
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        logger.error(f"Error reading CS quiz CSV: {e}")
        raise ValueError("CS quiz questions data not available.")

    domains = [
        "programming_score", "logical_score", "networking_score",
        "ai_score", "cyber_score", "communication_score"
    ]

    correct_counts = {dom: 0 for dom in domains}
    total_counts = {dom: 0 for dom in domains}
    total_correct = 0

    # Grade each answer
    for index, row in df.iterrows():
        q_id = f"q{index + 1}"
        csv_category = row["Category"]
        mapped_domain = CATEGORY_MAP.get(csv_category)

        if mapped_domain and mapped_domain in total_counts:
            total_counts[mapped_domain] += 1

        student_answer = answers.get(q_id)
        if student_answer:
            correct_answer = str(row["Correct_Answer"]).strip().upper()
            if student_answer.strip().upper() == correct_answer:
                total_correct += 1
                if mapped_domain and mapped_domain in correct_counts:
                    correct_counts[mapped_domain] += 1

    # Calculate percentage scores
    scores = {}
    for dom in domains:
        total = total_counts.get(dom, 0)
        correct = correct_counts.get(dom, 0)
        scores[dom] = round((correct / total) * 100.0, 2) if total > 0 else 0.0

    # Call career recommendation model
    try:
        recommendations = recommender.predict(scores)
    except Exception as e:
        logger.error(f"Error predicting career in CS quiz: {e}")
        recommendations = {
            "recommendations": []
        }

    return {
        "student_id": student_id,
        "total_questions": len(df),
        "total_correct": total_correct,
        "scores": scores,
        "recommendations": recommendations.get("recommendations", [])
    }
