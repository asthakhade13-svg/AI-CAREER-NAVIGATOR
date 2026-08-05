import logging
import os
from models.recommendation_model import recommender, personality_recommender
from utils.preprocess_openpsych import run_preprocessing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # 1. Run data preprocessing of the Holland Codes & Big Five datasets
    logger.info("Step 1: Running OpenPsychometrics data preprocessing pipeline...")
    try:
        run_preprocessing()
        logger.info("Data preprocessing completed successfully.")
    except Exception as e:
        logger.error(f"Data preprocessing failed: {e}")

    # 2. Train the Quiz Performance Recommender (Random Forest)
    logger.info("\nStep 2: Training Quiz Performance Recommender...")
    success_quiz = recommender.train("data/sample_students.csv")
    if success_quiz:
        logger.info("Quiz Performance Recommender trained successfully.")
        # Test sample quiz score prediction
        test_quiz_scores = {
            "programming_score": 85.0,
            "logical_score": 90.0,
            "networking_score": 40.0,
            "ai_score": 95.0,
            "cyber_score": 30.0,
            "communication_score": 70.0
        }
        try:
            pred_quiz = recommender.predict(test_quiz_scores)
            logger.info(f"Test Quiz prediction: {pred_quiz}")
        except Exception as e:
            logger.error(f"Test Quiz prediction failed: {e}")
    else:
        logger.error("Failed to train Quiz Performance Recommender.")

    # 3. Train the Personality & Aptitude Recommender (Random Forest)
    logger.info("\nStep 3: Training Personality & Aptitude Recommender...")
    success_pers = personality_recommender.train("data/preprocessed_psychometrics.csv")
    if success_pers:
        logger.info("Personality & Aptitude Recommender trained successfully.")
        # Test sample personality trait prediction
        test_traits = {
            "analytical_thinking": 85.0,
            "creativity": 75.0,
            "curiosity": 90.0,
            "attention_to_detail": 80.0,
            "communication": 60.0,
            "leadership": 50.0,
            "building_mindset": 70.0,
            "research_mindset": 88.0,
            "user_empathy": 65.0,
            "problem_solving": 82.0,
            "technical_depth": 83.0
        }
        try:
            pred_pers = personality_recommender.predict(test_traits)
            logger.info(f"Test Personality prediction (top 3): {pred_pers.get('recommendations', [])[:3]}")
        except Exception as e:
            logger.error(f"Test Personality prediction failed: {e}")
    else:
        logger.error("Failed to train Personality & Aptitude Recommender.")

    # 4. Print validation classification metrics if sklearn is available
    if not recommender.use_fallback and not personality_recommender.use_fallback:
        logger.info("\nStep 4: Running validation classification analysis...")
        try:
            import pandas as pd
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import classification_report

            df = pd.read_csv("data/preprocessed_psychometrics.csv")
            X = df[personality_recommender.feature_names]
            y = df["target_domain"]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Print evaluation report
            predictions = personality_recommender.model.predict(X_test)
            logger.info("\n=== Personality ML Model Evaluation Report ===")
            print(classification_report(y_test, predictions))
        except Exception as e:
            logger.warning(f"Failed to generate classification report: {e}")
