import joblib
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import logging

logger = logging.getLogger(__name__)


class RecommendationModel:
    def __init__(self, model_path="models_saved/career_rf_model.joblib"):
        self.model_path = model_path
        self.model = None
        self.feature_names = [
            "programming_score", "logical_score", "networking_score",
            "ai_score", "cyber_score", "communication_score"
        ]
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info("Recommendation model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
        else:
            logger.warning(f"Model not found at {self.model_path}. Please train the model first.")

    def train(self, data_path="data/sample_students.csv"):
        """Trains the Random Forest model using sample data."""
        try:
            df = pd.read_csv(data_path)
            X = df[self.feature_names]
            y = df["target_domain"]

            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X, y)

            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info(f"Model trained and saved to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False

    def predict(self, scores: dict):
        """Predicts the career domain based on scores."""
        if not self.model:
            raise ValueError("Model is not loaded or trained.")

        # Prepare input data
        input_data = pd.DataFrame([{
            feature: scores.get(feature, 0) for feature in self.feature_names
        }])

        # Predict probabilities
        probabilities = self.model.predict_proba(input_data)[0]
        classes = self.model.classes_

        # Combine classes and probabilities, sort descending
        results = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)

        # Return top 5 recommendations with confidence scores out of 100
        recommendations = [
            {"domain": domain, "score": round(prob * 100, 2)}
            for domain, prob in results[:5]
        ]

        return {"recommendations": recommendations}


# Singleton instance
recommender = RecommendationModel()
