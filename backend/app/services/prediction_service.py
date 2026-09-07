from pathlib import Path

import joblib
import pandas as pd
from app.database.db_collections import predictions_collection
from app.services.feature_service import FeatureService


class PredictionService:

    def __init__(self, feature_service: FeatureService):
        base_dir = Path(__file__).resolve().parents[3]

        model_path = (
            base_dir
            / "ml"
            / "models"
            / "random_forest_v4.pkl"
        )

        model_data = joblib.load(model_path)

        self.model = model_data["model"]
        self.feature_columns = model_data["features"]
        self.feature_service = feature_service

    def predict(
        self,
        home_team: str,
        away_team: str
    ):
        # Generate proper V4 features
        feature_dict = (
            self.feature_service.generate_features(
                home_team,
                away_team
            )
        )

        # Convert to DataFrame
        features = pd.DataFrame(
            [feature_dict]
        )

        # Make absolutely sure feature order
        # matches the trained model
        features = features[
            self.feature_columns
        ]

        # Check feature count
        if len(features.columns) != 100:
            raise ValueError(
                f"Expected 100 features, "
                f"got {len(features.columns)}"
            )

        # Predict probabilities
        probabilities = (
            self.model.predict_proba(features)[0]
        )

        classes = self.model.classes_

        probability_dict = {
            int(class_label): float(probability)
            for class_label, probability
            in zip(classes, probabilities)
        }

        predicted_class = int(
            classes[probabilities.argmax()]
        )

        class_names = {
            0: "Away Win",
            1: "Draw",
            2: "Home Win"
        }

        # Create prediction result
        result = {
            "home_team": home_team,
            "away_team": away_team,
            "prediction": class_names[
                predicted_class
            ],
            "probabilities": {
                "home": round(
                    probability_dict.get(2, 0.0),
                    4
                ),
                "draw": round(
                    probability_dict.get(1, 0.0),
                    4
                ),
                "away": round(
                    probability_dict.get(0, 0.0),
                    4
                ),
            }
        }

        # Save prediction to MongoDB
        predictions_collection.insert_one(result)

        # Return prediction to API
        return result