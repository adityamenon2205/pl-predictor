from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.container import prediction_service
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/predict", tags=["Prediction"])


@router.post("/", response_model=PredictionResponse)
def predict_match(request: PredictionRequest):
    try:
        result = prediction_service.predict(
            request.home_team,
            request.away_team
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))