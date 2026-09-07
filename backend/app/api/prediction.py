from app.services.prediction_history_service import PredictionHistoryService
from fastapi import APIRouter

router = APIRouter(
    prefix="/predictions",
    tags=["Prediction History"]
)

prediction_history_service = PredictionHistoryService()


@router.get("/")
def get_predictions():
    return {
        "predictions": prediction_history_service.get_predictions()
    }