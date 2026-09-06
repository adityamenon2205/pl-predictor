from pydantic import BaseModel


class PredictionRequest(BaseModel):
    home_team: str
    away_team: str


class PredictionResponse(BaseModel):
    home_team: str
    away_team: str
    prediction: str
    probabilities: dict[str, float]