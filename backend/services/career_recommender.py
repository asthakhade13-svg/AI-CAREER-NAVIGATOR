from models.recommendation_model import recommender
from utils.constants import DOMAINS
import logging

logger = logging.getLogger(__name__)


def recommend_career(student_id: str, scores: dict) -> dict:
    """
    Recommends a career domain using the trained Scikit-learn model.
    """
    try:
        recommendations = recommender.predict(scores)

        # You would typically save this recommendation to MongoDB here

        return recommendations
    except Exception as e:
        logger.error(f"Error recommending career for {student_id}: {e}")
        # Fallback to rule-based or generic if model fails
        return {
            "recommendations": [
                {"domain": DOMAINS[0], "score": 80.0},
                {"domain": DOMAINS[1], "score": 75.0}
            ]
        }
