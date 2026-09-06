from app.services.container import feature_service
from fastapi import APIRouter

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)


@router.get("/")
def get_teams():
    return {
        "teams": feature_service.teams
    }