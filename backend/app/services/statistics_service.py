from pathlib import Path

import pandas as pd


class StatisticsService:
    def __init__(self):
        base_dir = Path(__file__).resolve().parents[3]
        data_path = base_dir / "ml" / "data" / "processed" / "epl_matches.csv"

        self.df = pd.read_csv(data_path)

    def get_overall_statistics(self):
        total_matches = len(self.df)

        home_wins = (self.df["FTR"] == "H").sum()
        draws = (self.df["FTR"] == "D").sum()
        away_wins = (self.df["FTR"] == "A").sum()

        return {
            "total_matches": int(total_matches),
            "home_wins": int(home_wins),
            "draws": int(draws),
            "away_wins": int(away_wins),
            "home_win_percentage": round(home_wins / total_matches * 100, 2),
            "draw_percentage": round(draws / total_matches * 100, 2),
            "away_win_percentage": round(away_wins / total_matches * 100, 2)
        }