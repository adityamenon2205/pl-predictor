from pathlib import Path

import pandas as pd
from app.database.db_collections import matches_collection, teams_collection


def seed_database():
    # Project root: pl-predictor/
    base_dir = Path(__file__).resolve().parents[3]

    data_path = (
        base_dir
        / "ml"
        / "data"
        / "processed"
        / "epl_matches.csv"
    )

    # Load cleaned EPL data
    df = pd.read_csv(data_path)

    # Clear existing data
    matches_collection.delete_many({})
    teams_collection.delete_many({})

    # Convert DataFrame records to dictionaries
    matches = df.to_dict(orient="records")

    # Insert matches
    if matches:
        matches_collection.insert_many(matches)

    # Get unique teams
    teams = sorted(
        set(df["HomeTeam"].dropna())
        | set(df["AwayTeam"].dropna())
    )

    team_documents = [
        {"name": team}
        for team in teams
    ]

    if team_documents:
        teams_collection.insert_many(team_documents)

    print(f"Inserted {len(matches)} matches")
    print(f"Inserted {len(team_documents)} teams")


if __name__ == "__main__":
    seed_database()