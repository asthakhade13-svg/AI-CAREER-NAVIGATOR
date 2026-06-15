import google.generativeai as genai
from config import settings
import json
import logging
from utils.helpers import save_json
import os
import requests

logger = logging.getLogger(__name__)

# Configure Gemini if available
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
elif not settings.GROK_API_KEY:
    logger.warning("Neither GEMINI_API_KEY nor GROK_API_KEY is set. Quiz generator will not work.")


def generate_quiz(topic: str, content: str) -> dict:
    """
    Uses Grok or Gemini API to generate a quiz based on the topic and content.
    Returns structured JSON.
    """
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

    # 1. Try Grok or Groq first if key is present
    if settings.GROK_API_KEY:
        try:
            # Check if it is a Groq key (starts with gsk_) or Grok key
            if settings.GROK_API_KEY.startswith("gsk_"):
                api_url = "https://api.groq.com/openai/v1/chat/completions"
                model_name = "llama-3.3-70b-versatile"
                logger.info("Using Groq API for quiz generation")
            else:
                api_url = "https://api.x.ai/v1/chat/completions"
                model_name = "grok-2-1212"
                logger.info("Using Grok API for quiz generation")

            headers = {
                "Authorization": f"Bearer {settings.GROK_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            res = requests.post(api_url, headers=headers, json=payload, timeout=15)
            if res.ok:
                response_text = res.json()["choices"][0]["message"]["content"].strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:-3].strip()
                elif response_text.startswith("```"):
                    response_text = response_text[3:-3].strip()
                return json.loads(response_text)
            else:
                logger.error(f"External API error ({model_name}) in quiz gen: {res.status_code} - {res.text}")
        except Exception as e:
            logger.error(f"Error generating quiz using external API: {e}")

    # 2. Fallback to Gemini
    if not settings.GEMINI_API_KEY:
        raise ValueError("Neither Grok nor Gemini API key is configured.")

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
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
        logger.error(f"Error generating quiz using Gemini for {topic}: {e}")
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


def generate_options_for_question(question: str, career_field: str, difficulty: str) -> dict:
    """
    Generates 4 distinct options and correct_answer for a question using LLM (Groq/Grok/Gemini).
    """
    prompt = f"""You are a Computer Science expert. For the following question in the domain of '{career_field}' (Difficulty: {difficulty}), generate 4 distinct, plausible multiple-choice options (A, B, C, D) and identify which one is correct.

Question: {question}

Return the response ONLY as a JSON object matching this structure:
{{
  "options": {{
    "A": "Option A text",
    "B": "Option B text",
    "C": "Option C text",
    "D": "Option D text"
  }},
  "correct_answer": "A"
}}
"""
    # Try Grok/Groq first
    if settings.GROK_API_KEY:
        try:
            if settings.GROK_API_KEY.startswith("gsk_"):
                api_url = "https://api.groq.com/openai/v1/chat/completions"
                model_name = "llama-3.3-70b-versatile"
            else:
                api_url = "https://api.x.ai/v1/chat/completions"
                model_name = "grok-2-1212"

            headers = {
                "Authorization": f"Bearer {settings.GROK_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            res = requests.post(api_url, headers=headers, json=payload, timeout=8)
            if res.ok:
                response_text = res.json()["choices"][0]["message"]["content"].strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:-3].strip()
                elif response_text.startswith("```"):
                    response_text = response_text[3:-3].strip()
                return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error in dynamic option generation (Grok/Groq): {e}")

    # Fallback to Gemini
    if settings.GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error in dynamic option generation (Gemini): {e}")

    return {}
