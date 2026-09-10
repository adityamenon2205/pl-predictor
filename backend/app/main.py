from app.api.prediction import router as prediction_router
from app.api.predictions import router as predictions_router
from app.api.statistics import router as statistics_router
from app.api.teams import router as teams_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Premier League Match Predictor",
    description="ML-powered Premier League match outcome prediction API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prediction_router)
app.include_router(predictions_router)
app.include_router(teams_router)
app.include_router(statistics_router)


@app.get("/")
def root():
    return {
        "message": "Premier League Predictor API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }