from app.services.statistics_service import StatisticsService
from fastapi import APIRouter

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"]
)

statistics_service = StatisticsService()


@router.get("/")
def get_statistics():
    return statistics_service.get_overall_statistics()