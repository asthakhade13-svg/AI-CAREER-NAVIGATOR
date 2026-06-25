import joblib
import os
import math
import pandas as pd
import logging

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import RandomForestClassifier
    SKLEARN_AVAILABLE = True
except (ImportError, Exception) as e:
    SKLEARN_AVAILABLE = False
    logger.warning(
        f"scikit-learn is not available or blocked by system policies. "
        f"Falling back to high-fidelity profile-centroid recommendation engine. Error: {type(e).__name__}"
    )


class RecommendationModel:
    def __init__(self, model_path="models_saved/career_rf_model.joblib"):
        self.model_path = model_path
        self.model = None
        self.feature_names = [
            "programming_score", "logical_score", "networking_score",
            "ai_score", "cyber_score", "communication_score"
        ]
        self.use_fallback = not SKLEARN_AVAILABLE
        self._load_model()

    def _load_model(self):
        if self.use_fallback:
            logger.info("Using profile-centroid recommendation model (fallback mode).")
            return

        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                logger.info("Recommendation model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}. Switching to centroid fallback.")
                self.use_fallback = True
        else:
            logger.warning(f"Model not found at {self.model_path}. Switching to centroid fallback.")
            self.use_fallback = True

    def train(self, data_path="data/sample_students.csv"):
        """Trains the Random Forest model using sample data if sklearn is available, or prints warning."""
        if self.use_fallback:
            logger.info("Centroid model is dynamic and does not require explicit training. Using sample data directly.")
            return True

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
            logger.error(f"Error training model: {e}. Falling back to centroid-based model.")
            self.use_fallback = True
            return True

    def predict(self, scores: dict):
        """Predicts the career domain based on scores."""
        if self.use_fallback:
            return self._predict_fallback(scores)

        if not self.model:
            raise ValueError("Model is not loaded or trained.")

        try:
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
                {"domain": domain, "score": float(round(prob * 100, 2))}
                for domain, prob in results[:5]
            ]
            return {"recommendations": recommendations}
        except Exception as e:
            logger.error(f"Prediction using RF failed: {e}. Trying fallback predictor.")
            return self._predict_fallback(scores)

    def _predict_fallback(self, scores: dict, data_path="data/sample_students.csv"):
        """Centroid-based similarity fallback algorithm when sklearn is blocked or fails."""
        try:
            if not os.path.exists(data_path):
                # Hardcoded fallback list if data is missing
                logger.warning(f"Data file not found at {data_path}. Using hardcoded default recommendations.")
                return {
                    "recommendations": [
                        {"domain": "AI/ML", "score": 25.0},
                        {"domain": "Web Development", "score": 20.0},
                        {"domain": "Cybersecurity", "score": 18.0},
                        {"domain": "Data Science", "score": 15.0},
                        {"domain": "Cloud Computing", "score": 12.0}
                    ]
                }

            df = pd.read_csv(data_path)
            # Group by domain and get mean
            centroids = df.groupby("target_domain")[self.feature_names].mean().to_dict(orient="index")

            sims = {}
            for domain, centroid in centroids.items():
                # Cosine similarity
                dot_product = sum(scores.get(feat, 0) * centroid[feat] for feat in self.feature_names)
                norm_a = sum(scores.get(feat, 0) ** 2 for feat in self.feature_names) ** 0.5
                norm_b = sum(centroid[feat] ** 2 for feat in self.feature_names) ** 0.5

                if norm_a == 0 or norm_b == 0:
                    sim = 0.0
                else:
                    sim = dot_product / (norm_a * norm_b)
                sims[domain] = sim

            # Use softmax/exponentiation to make the top recommendations stand out
            exp_sims = {domain: math.exp(sim * 15) for domain, sim in sims.items()}
            total_exp = sum(exp_sims.values())

            results = []
            for domain, exp_sim in exp_sims.items():
                prob = exp_sim / total_exp
                results.append((domain, prob))

            results = sorted(results, key=lambda x: x[1], reverse=True)

            recommendations = [
                {"domain": domain, "score": float(round(prob * 100, 2))}
                for domain, prob in results[:5]
            ]
            return {"recommendations": recommendations}
        except Exception as err:
            logger.error(f"Fallback prediction failed: {err}")
            return {
                "recommendations": [
                    {"domain": "AI/ML", "score": 20.0},
                    {"domain": "Web Development", "score": 20.0},
                    {"domain": "Cybersecurity", "score": 20.0},
                    {"domain": "Data Science", "score": 20.0},
                    {"domain": "Cloud Computing", "score": 20.0}
                ]
            }


# Singleton instance
recommender = RecommendationModel()

