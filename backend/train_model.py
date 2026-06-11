import logging
from models.recommendation_model import recommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting ML model training...")
    success = recommender.train("data/sample_students.csv")
    if success:
        logger.info("Training completed successfully.")

        # Test a prediction
        test_scores = {
            "programming_score": 85,
            "logical_score": 90,
            "networking_score": 40,
            "ai_score": 95,
            "cyber_score": 30,
            "communication_score": 70
        }
        logger.info(f"Testing prediction with scores: {test_scores}")
        try:
            pred = recommender.predict(test_scores)
            logger.info(f"Prediction result: {pred}")
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
    else:
        logger.error("Training failed.")
