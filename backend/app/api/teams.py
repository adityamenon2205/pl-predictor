from app.database.db_collections import teams_collection
from app.services.container import feature_service
from fastapi import APIRouter

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)


@router.get("/")
def get_teams():
    teams = teams_collection.find(
        {},
        {"_id": 0, "name": 1}
    )

    return {
        "teams": [team["name"] for team in teams]
    }