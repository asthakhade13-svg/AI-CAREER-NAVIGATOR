import google.generativeai as genai
from config import settings
import json
import logging
from utils.helpers import save_json
import os

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY is not set. Quiz generator will not work.")


def generate_quiz(topic: str, content: str) -> dict:
    """
    Uses Gemini API to generate a quiz based on the topic and content.
    Returns structured JSON.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key is missing.")

    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    You are an expert Computer Science professor. Create a quiz based on the following learning material.
    Topic: {topic}
    Content: {content}

    Generate exactly:
    - 5 Easy MCQs
    - 3 Medium MCQs
    - 2 Hard MCQs
    - 2 True/False questions
    - 1 Fill-in-the-blank question

    Return the response ONLY as a valid JSON object matching this structure (no markdown tags, no backticks, just the JSON string):
    {{
      "topic": "{topic}",
      "mcqs": [
        {{
          "question": "string",
          "options": ["string", "string", "string", "string"],
          "correct_answer": "string",
          "difficulty": "Easy/Medium/Hard",
          "topic_tag": "{topic}"
        }}
      ],
      "true_false": [
        {{
          "question": "string",
          "correct_answer": "True/False",
          "difficulty": "Easy/Medium/Hard",
          "topic_tag": "{topic}"
        }}
      ],
      "fill_in_blanks": [
        {{
          "question": "string",
          "correct_answer": "string",
          "difficulty": "Easy/Medium/Hard",
          "topic_tag": "{topic}"
        }}
      ]
    }}
    """

    try:
        response = model.generate_content(prompt)
        # Clean the response to ensure it's pure JSON
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()

        quiz_data = json.loads(response_text)
        return quiz_data
    except Exception as e:
        logger.error(f"Error generating quiz for {topic}: {e}")
        raise


def batch_generate_quizzes(df):
    """
    Generates quizzes for an entire DataFrame and saves them.
    """
    all_quizzes = []
    for index, row in df.iterrows():
        try:
            logger.info(f"Generating quiz for {row['topic']}...")
            quiz = generate_quiz(row['topic'], row['content'])
            all_quizzes.append(quiz)
        except Exception as e:
            logger.error(f"Failed to generate quiz for {row['topic']}: {e}")

    # Save to output
    os.makedirs("output", exist_ok=True)
    save_json(all_quizzes, "output/generated_quizzes.json")
    return all_quizzes
