from app.services.feature_service import FeatureService
from app.services.prediction_service import PredictionService

feature_service = FeatureService()
prediction_service = PredictionService(feature_service)