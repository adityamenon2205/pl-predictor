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
                (home_wins / total_matches) * 100,
                2
            ),
            "draw_percentage": round(
                (draws / total_matches) * 100,
                2
            ),
            "away_win_percentage": round(
                (away_wins / total_matches) * 100,
                2
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

        goal_difference = (
            goals_scored - goals_conceded
        )

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
                win_percentage,
                2
            ),

            "draw_percentage": round(
                draw_percentage,
                2
            ),

            "loss_percentage": round(
                loss_percentage,
                2
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

    # =========================================
    # LEAGUE ANALYTICS
    # =========================================

    def get_league_analytics(self):

        matches = list(
            matches_collection.find(
                {},
                {
                    "_id": 0,
                    "Season": 1,
                    "HomeTeam": 1,
                    "AwayTeam": 1,
                    "FTHG": 1,
                    "FTAG": 1,
                    "FTR": 1,
                }
            )
        )

        if not matches:
            return {
                "season_trends": [],
                "overall": {},
                "team_rankings": [],
            }

        # =========================================
        # SEASON AGGREGATION
        # =========================================

        seasons = {}

        for match in matches:

            season = match.get("Season")

            if season not in seasons:
                seasons[season] = {
                    "matches": 0,
                    "home_wins": 0,
                    "draws": 0,
                    "away_wins": 0,
                    "home_goals": 0,
                    "away_goals": 0,
                }

            season_data = seasons[season]

            season_data["matches"] += 1

            season_data["home_goals"] += match["FTHG"]
            season_data["away_goals"] += match["FTAG"]

            if match["FTR"] == "H":
                season_data["home_wins"] += 1

            elif match["FTR"] == "D":
                season_data["draws"] += 1

            elif match["FTR"] == "A":
                season_data["away_wins"] += 1

        # =========================================
        # SEASON TRENDS
        # =========================================

        season_trends = []

        for season, data in seasons.items():

            matches_count = data["matches"]

            total_goals = (
                data["home_goals"]
                + data["away_goals"]
            )

            season_trends.append({
                "season": season,

                "matches": matches_count,

                "home_wins": data["home_wins"],
                "draws": data["draws"],
                "away_wins": data["away_wins"],

                "home_win_percentage": round(
                    (
                        data["home_wins"]
                        / matches_count
                    ) * 100,
                    2
                ),

                "draw_percentage": round(
                    (
                        data["draws"]
                        / matches_count
                    ) * 100,
                    2
                ),

                "away_win_percentage": round(
                    (
                        data["away_wins"]
                        / matches_count
                    ) * 100,
                    2
                ),

                "home_goals": data["home_goals"],
                "away_goals": data["away_goals"],
                "total_goals": total_goals,

                "goals_per_match": round(
                    total_goals
                    / matches_count,
                    2
                ),

                "home_goals_per_match": round(
                    data["home_goals"]
                    / matches_count,
                    2
                ),

                "away_goals_per_match": round(
                    data["away_goals"]
                    / matches_count,
                    2
                ),
            })

        # =========================================
        # SORT SEASONS
        # =========================================

        season_trends.sort(
            key=lambda item: str(item["season"])
        )

        # =========================================
        # OVERALL LEAGUE METRICS
        # =========================================

        total_matches = len(matches)

        total_home_goals = sum(
            match["FTHG"]
            for match in matches
        )

        total_away_goals = sum(
            match["FTAG"]
            for match in matches
        )

        total_goals = (
            total_home_goals
            + total_away_goals
        )

        home_wins = sum(
            1
            for match in matches
            if match["FTR"] == "H"
        )

        draws = sum(
            1
            for match in matches
            if match["FTR"] == "D"
        )

        away_wins = sum(
            1
            for match in matches
            if match["FTR"] == "A"
        )

        # =========================================
        # TEAM RANKINGS
        # =========================================

        teams = {}

        for match in matches:

            home_team = match["HomeTeam"]
            away_team = match["AwayTeam"]

            home_goals = match["FTHG"]
            away_goals = match["FTAG"]

            # Initialize teams

            if home_team not in teams:
                teams[home_team] = {
                    "team": home_team,
                    "matches": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "goals_scored": 0,
                    "goals_conceded": 0,
                }

            if away_team not in teams:
                teams[away_team] = {
                    "team": away_team,
                    "matches": 0,
                    "wins": 0,
                    "draws": 0,
                    "losses": 0,
                    "goals_scored": 0,
                    "goals_conceded": 0,
                }

            home = teams[home_team]
            away = teams[away_team]

            # Matches

            home["matches"] += 1
            away["matches"] += 1

            # Goals

            home["goals_scored"] += home_goals
            home["goals_conceded"] += away_goals

            away["goals_scored"] += away_goals
            away["goals_conceded"] += home_goals

            # Results

            if match["FTR"] == "H":

                home["wins"] += 1
                away["losses"] += 1

            elif match["FTR"] == "D":

                home["draws"] += 1
                away["draws"] += 1

            elif match["FTR"] == "A":

                home["losses"] += 1
                away["wins"] += 1

        # =========================================
        # FORMAT TEAM RANKINGS
        # =========================================

        team_rankings = []

        for team_data in teams.values():

            matches_played = team_data["matches"]

            goal_difference = (
                team_data["goals_scored"]
                - team_data["goals_conceded"]
            )

            points = (
                team_data["wins"] * 3
                + team_data["draws"]
            )

            win_percentage = (
                team_data["wins"]
                / matches_played
            ) * 100

            team_rankings.append({
                "team": team_data["team"],
                "matches": matches_played,
                "wins": team_data["wins"],
                "draws": team_data["draws"],
                "losses": team_data["losses"],
                "goals_scored": team_data["goals_scored"],
                "goals_conceded": team_data["goals_conceded"],
                "goal_difference": goal_difference,
                "points": points,
                "win_percentage": round(
                    win_percentage,
                    2
                ),
            })

        # Sort by points, then goal difference,
        # then goals scored.

        team_rankings.sort(
            key=lambda team: (
                team["points"],
                team["goal_difference"],
                team["goals_scored"],
            ),
            reverse=True
        )

        # Add rank after sorting.

        for index, team in enumerate(
            team_rankings,
            start=1
        ):
            team["rank"] = index

        # =========================================
        # FINAL RESPONSE
        # =========================================

        return {
            "overall": {
                "total_matches": total_matches,

                "home_wins": home_wins,
                "draws": draws,
                "away_wins": away_wins,

                "home_win_percentage": round(
                    (
                        home_wins
                        / total_matches
                    ) * 100,
                    2
                ),

                "draw_percentage": round(
                    (
                        draws
                        / total_matches
                    ) * 100,
                    2
                ),

                "away_win_percentage": round(
                    (
                        away_wins
                        / total_matches
                    ) * 100,
                    2
                ),

                "total_goals": total_goals,

                "home_goals": total_home_goals,
                "away_goals": total_away_goals,

                "goals_per_match": round(
                    total_goals
                    / total_matches,
                    2
                ),

                "home_goals_per_match": round(
                    total_home_goals
                    / total_matches,
                    2
                ),

                "away_goals_per_match": round(
                    total_away_goals
                    / total_matches,
                    2
                ),
            },

            "season_trends": season_trends,

            "team_rankings": team_rankings,
        }