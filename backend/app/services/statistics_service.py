from app.database.db_collections import matches_collection


class StatisticsService:

    def get_overall_statistics(self):
        total_matches = matches_collection.count_documents({})

        home_wins = matches_collection.count_documents({
            "FTR": "H"
        })

        draws = matches_collection.count_documents({
            "FTR": "D"
        })

        away_wins = matches_collection.count_documents({
            "FTR": "A"
        })

        if total_matches == 0:
            return {
                "total_matches": 0,
                "home_wins": 0,
                "draws": 0,
                "away_wins": 0,
                "home_win_percentage": 0,
                "draw_percentage": 0,
                "away_win_percentage": 0,
            }

        return {
            "total_matches": total_matches,
            "home_wins": home_wins,
            "draws": draws,
            "away_wins": away_wins,
            "home_win_percentage": round(
                (home_wins / total_matches) * 100, 2
            ),
            "draw_percentage": round(
                (draws / total_matches) * 100, 2
            ),
            "away_win_percentage": round(
                (away_wins / total_matches) * 100, 2
            ),
        }

    def get_team_statistics(self, team_name: str):

        # Find all matches involving this team
        matches = list(
            matches_collection.find(
                {
                    "$or": [
                        {"HomeTeam": team_name},
                        {"AwayTeam": team_name},
                    ]
                },
                {
                    "_id": 0
                }
            )
        )

        if not matches:
            raise ValueError(
                f"No matches found for team: {team_name}"
            )

        matches_played = len(matches)

        wins = 0
        draws = 0
        losses = 0

        goals_scored = 0
        goals_conceded = 0

        home_matches = 0
        home_wins = 0
        home_draws = 0
        home_losses = 0

        away_matches = 0
        away_wins = 0
        away_draws = 0
        away_losses = 0

        for match in matches:

            home_team = match["HomeTeam"]
            away_team = match["AwayTeam"]

            home_goals = match["FTHG"]
            away_goals = match["FTAG"]

            # --------------------------------
            # TEAM PLAYING AT HOME
            # --------------------------------

            if home_team == team_name:

                home_matches += 1

                goals_scored += home_goals
                goals_conceded += away_goals

                if match["FTR"] == "H":
                    wins += 1
                    home_wins += 1

                elif match["FTR"] == "D":
                    draws += 1
                    home_draws += 1

                elif match["FTR"] == "A":
                    losses += 1
                    home_losses += 1

            # --------------------------------
            # TEAM PLAYING AWAY
            # --------------------------------

            else:

                away_matches += 1

                goals_scored += away_goals
                goals_conceded += home_goals

                if match["FTR"] == "A":
                    wins += 1
                    away_wins += 1

                elif match["FTR"] == "D":
                    draws += 1
                    away_draws += 1

                elif match["FTR"] == "H":
                    losses += 1
                    away_losses += 1

        losses = matches_played - wins - draws

        goal_difference = goals_scored - goals_conceded

        win_percentage = (
            (wins / matches_played) * 100
        )

        draw_percentage = (
            (draws / matches_played) * 100
        )

        loss_percentage = (
            (losses / matches_played) * 100
        )

        return {
            "team": team_name,

            "matches_played": matches_played,

            "wins": wins,
            "draws": draws,
            "losses": losses,

            "win_percentage": round(
                win_percentage, 2
            ),

            "draw_percentage": round(
                draw_percentage, 2
            ),

            "loss_percentage": round(
                loss_percentage, 2
            ),

            "goals_scored": goals_scored,
            "goals_conceded": goals_conceded,
            "goal_difference": goal_difference,

            "home": {
                "matches": home_matches,
                "wins": home_wins,
                "draws": home_draws,
                "losses": home_losses,
            },

            "away": {
                "matches": away_matches,
                "wins": away_wins,
                "draws": away_draws,
                "losses": away_losses,
            },
        }