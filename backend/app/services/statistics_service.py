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
                "away_win_percentage": 0
            }

        return {
            "total_matches": total_matches,
            "home_wins": home_wins,
            "draws": draws,
            "away_wins": away_wins,
            "home_win_percentage": round(
                home_wins / total_matches * 100, 2
            ),
            "draw_percentage": round(
                draws / total_matches * 100, 2
            ),
            "away_win_percentage": round(
                away_wins / total_matches * 100, 2
            )
        }