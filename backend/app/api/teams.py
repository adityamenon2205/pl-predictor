from app.database.db_collections import teams_collection
from app.services.statistics_service import StatisticsService
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/teams",
    tags=["Teams"]
)

statistics_service = StatisticsService()


@router.get("/")
def get_teams():

    teams = teams_collection.find(
        {},
        {
            "_id": 0,
            "name": 1
        }
    )

    return {
        "teams": [
            team["name"]
            for team in teams
        ]
    }


@router.get("/{team_name}/statistics")
def get_team_statistics(team_name: str):

    try:

        return statistics_service.get_team_statistics(
            team_name
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )