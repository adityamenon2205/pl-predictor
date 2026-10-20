
from app.services.prediction_history_service import (
    PredictionHistoryService,
)
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/predictions",
    tags=["Prediction History"],
)

prediction_history_service = PredictionHistoryService()


@router.get("/")
def get_predictions():
    return {
        "predictions": prediction_history_service.get_predictions()
    }


@router.delete("/")
def clear_predictions():
    try:
        deleted_count = prediction_history_service.clear_predictions()

        return {
            "message": "Prediction history cleared successfully.",
            "deleted_count": deleted_count,
        }
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Failed to clear prediction history.",
        )
