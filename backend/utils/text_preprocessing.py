import re
from typing import List


def clean_text(text: str) -> str:
    """
    Removes extra whitespace and special characters from text.
    """
    if not isinstance(text, str):
        return ""

    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,?!-]', '', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def chunk_text(text: str, max_words: int = 500) -> List[str]:
    """
    Splits long content into manageable chunks of words.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks
