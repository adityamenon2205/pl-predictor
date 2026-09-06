from collections import defaultdict, deque
from pathlib import Path

import numpy as np
import pandas as pd


class FeatureService:

    INITIAL_ELO = 1500
    ELO_K = 20
    HOME_ELO_ADVANTAGE = 60
    FORM_WINDOWS = [3, 5, 10]  # noqa: RUF012

    def __init__(self):
        base_dir = Path(__file__).resolve().parents[3]

        self.data_path = (
            base_dir
            / "ml"
            / "data"
            / "processed"
            / "epl_matches.csv"
        )

        self.df = pd.read_csv(self.data_path)

        self.df["Date"] = pd.to_datetime(self.df["Date"])

        self.df = (
            self.df
            .sort_values(["Date", "Season"])
            .reset_index(drop=True)
        )

        self.teams = sorted(
            set(self.df["HomeTeam"])
            | set(self.df["AwayTeam"])
        )

         # Build historical team state once.
        # This avoids recalculating the entire dataset
        # for every prediction request.
        (
            self.team_history,
            self.home_history,
            self.away_history,
            self.elo,
            self.last_match_date
        ) = self.build_team_state()
    # ==========================================================
    # BASIC HELPERS
    # ==========================================================

    @staticmethod
    def safe_average(values):
        return np.mean(values) if values else 0.0

    def get_form_stats(self, history, window):

        recent = list(history)[-window:]

        if not recent:
            return {
                "points": 0.0,
                "ppg": 0.0,
                "win_rate": 0.0,
                "goals_scored": 0.0,
                "goals_conceded": 0.0,
                "goal_difference": 0.0,
                "shots": 0.0,
                "shots_on_target": 0.0,
                "corners": 0.0,
            }

        points = [x["points"] for x in recent]

        return {
            "points": sum(points),
            "ppg": self.safe_average(points),
            "win_rate": sum(
                x["points"] == 3 for x in recent
            ) / len(recent),
            "goals_scored": self.safe_average(
                [x["goals_scored"] for x in recent]
            ),
            "goals_conceded": self.safe_average(
                [x["goals_conceded"] for x in recent]
            ),
            "goal_difference": self.safe_average(
                [
                    x["goals_scored"] - x["goals_conceded"]
                    for x in recent
                ]
            ),
            "shots": self.safe_average(
                [x["shots"] for x in recent]
            ),
            "shots_on_target": self.safe_average(
                [x["shots_on_target"] for x in recent]
            ),
            "corners": self.safe_average(
                [x["corners"] for x in recent]
            ),
        }

    @staticmethod
    def get_venue_stats(history):

        if not history:
            return {
                "win_rate": 0.0,
                "goals_scored": 0.0,
                "goals_conceded": 0.0,
                "ppg": 0.0,
            }

        return {
            "win_rate": sum(
                x["points"] == 3 for x in history
            ) / len(history),

            "goals_scored": np.mean(
                [x["goals_scored"] for x in history]
            ),

            "goals_conceded": np.mean(
                [x["goals_conceded"] for x in history]
            ),

            "ppg": np.mean(
                [x["points"] for x in history]
            ),
        }

    # ==========================================================
    # ELO
    # ==========================================================

    def elo_expected(self, elo_home, elo_away):

        difference = (
            elo_away
            - (elo_home + self.HOME_ELO_ADVANTAGE)
        ) / 400

        return 1 / (1 + 10 ** difference)

    def update_elo(
        self,
        home_elo,
        away_elo,
        result
    ):

        expected_home = self.elo_expected(
            home_elo,
            away_elo
        )

        if result == "H":
            actual_home = 1.0
        elif result == "D":
            actual_home = 0.5
        else:
            actual_home = 0.0

        change = self.ELO_K * (
            actual_home - expected_home
        )

        return (
            home_elo + change,
            away_elo - change
        )

    # ==========================================================
    # BUILD CURRENT TEAM STATE
    # ==========================================================

    def build_team_state(self):

        team_history = defaultdict(
            lambda: deque(maxlen=10)
        )

        home_history = defaultdict(list)
        away_history = defaultdict(list)

        elo = defaultdict(
            lambda: self.INITIAL_ELO
        )

        last_match_date = {}

        for _, match in self.df.iterrows():

            date = match["Date"]
            home = match["HomeTeam"]
            away = match["AwayTeam"]

            # Current state BEFORE this match
            # is what was used by the training pipeline.

            home_elo = elo[home]
            away_elo = elo[away]

            # Match result
            result = match["FTR"]

            if result == "H":
                home_points = 3
                away_points = 0
            elif result == "D":
                home_points = 1
                away_points = 1
            else:
                home_points = 0
                away_points = 3

            home_record = {
                "points": home_points,
                "goals_scored": match["FTHG"],
                "goals_conceded": match["FTAG"],
                "shots": match["HS"],
                "shots_on_target": match["HST"],
                "corners": match["HC"],
            }

            away_record = {
                "points": away_points,
                "goals_scored": match["FTAG"],
                "goals_conceded": match["FTHG"],
                "shots": match["AS"],
                "shots_on_target": match["AST"],
                "corners": match["AC"],
            }

            team_history[home].append(home_record)
            team_history[away].append(away_record)

            home_history[home].append(home_record)
            away_history[away].append(away_record)

            # Update Elo AFTER match
            new_home_elo, new_away_elo = self.update_elo(
                home_elo,
                away_elo,
                result
            )

            elo[home] = new_home_elo
            elo[away] = new_away_elo

            last_match_date[home] = date
            last_match_date[away] = date

        return (
            team_history,
            home_history,
            away_history,
            elo,
            last_match_date
        )

    # ==========================================================
    # GENERATE MATCH FEATURES
    # ==========================================================

    def generate_features(
        self,
        home_team,
        away_team
    ):

        if home_team not in self.teams:
            raise ValueError(
                f"Unknown home team: {home_team}"
            )

        if away_team not in self.teams:
            raise ValueError(
                f"Unknown away team: {away_team}"
            )

        if home_team == away_team:
            raise ValueError(
                "Home and away teams must be different"
            )

        # Use cached historical state
        team_history = self.team_history
        home_history = self.home_history
        away_history = self.away_history
        elo = self.elo
        last_match_date = self.last_match_date

        # ------------------------------------------------------
        # Current team state
        # ------------------------------------------------------

        home_form = {
            window: self.get_form_stats(
                team_history[home_team],
                window
            )
            for window in self.FORM_WINDOWS
        }

        away_form = {
            window: self.get_form_stats(
                team_history[away_team],
                window
            )
            for window in self.FORM_WINDOWS
        }

        home_venue = self.get_venue_stats(
            home_history[home_team]
        )

        away_venue = self.get_venue_stats(
            away_history[away_team]
        )

        home_elo = elo[home_team]
        away_elo = elo[away_team]

        # Use the latest match date in our dataset
        latest_date = self.df["Date"].max()

        home_rest = (
            (latest_date - last_match_date[home_team]).days
            if home_team in last_match_date
            else 0
        )

        away_rest = (
            (latest_date - last_match_date[away_team]).days
            if away_team in last_match_date
            else 0
        )

        # ------------------------------------------------------
        # Neutral market fallback
        # ------------------------------------------------------

        market_home = 1 / 3
        market_draw = 1 / 3
        market_away = 1 / 3

        market_margin = 1.0

        # ------------------------------------------------------
        # V3 FEATURES
        # ------------------------------------------------------

        features = {

            # Home form
            "home_form_points_3": home_form[3]["points"],
            "home_form_points_5": home_form[5]["points"],
            "home_form_points_10": home_form[10]["points"],

            "home_ppg_3": home_form[3]["ppg"],
            "home_ppg_5": home_form[5]["ppg"],
            "home_ppg_10": home_form[10]["ppg"],

            "home_win_rate_3": home_form[3]["win_rate"],
            "home_win_rate_5": home_form[5]["win_rate"],
            "home_win_rate_10": home_form[10]["win_rate"],

            "home_goals_scored_3":
                home_form[3]["goals_scored"],
            "home_goals_scored_5":
                home_form[5]["goals_scored"],
            "home_goals_scored_10":
                home_form[10]["goals_scored"],

            "home_goals_conceded_3":
                home_form[3]["goals_conceded"],
            "home_goals_conceded_5":
                home_form[5]["goals_conceded"],
            "home_goals_conceded_10":
                home_form[10]["goals_conceded"],

            "home_goal_diff_5":
                home_form[5]["goal_difference"],
            "home_goal_diff_10":
                home_form[10]["goal_difference"],

            "home_shots_avg":
                home_form[5]["shots"],
            "home_shots_on_target_avg":
                home_form[5]["shots_on_target"],
            "home_corners_avg":
                home_form[5]["corners"],

            # Away form
            "away_form_points_3": away_form[3]["points"],
            "away_form_points_5": away_form[5]["points"],
            "away_form_points_10": away_form[10]["points"],

            "away_ppg_3": away_form[3]["ppg"],
            "away_ppg_5": away_form[5]["ppg"],
            "away_ppg_10": away_form[10]["ppg"],

            "away_win_rate_3":
                away_form[3]["win_rate"],
            "away_win_rate_5":
                away_form[5]["win_rate"],
            "away_win_rate_10":
                away_form[10]["win_rate"],

            "away_goals_scored_3":
                away_form[3]["goals_scored"],
            "away_goals_scored_5":
                away_form[5]["goals_scored"],
            "away_goals_scored_10":
                away_form[10]["goals_scored"],

            "away_goals_conceded_3":
                away_form[3]["goals_conceded"],
            "away_goals_conceded_5":
                away_form[5]["goals_conceded"],
            "away_goals_conceded_10":
                away_form[10]["goals_conceded"],

            "away_goal_diff_5":
                away_form[5]["goal_difference"],
            "away_goal_diff_10":
                away_form[10]["goal_difference"],

            "away_shots_avg":
                away_form[5]["shots"],
            "away_shots_on_target_avg":
                away_form[5]["shots_on_target"],
            "away_corners_avg":
                away_form[5]["corners"],

            # Differences
            "form_points_diff":
                home_form[5]["points"]
                - away_form[5]["points"],

            "ppg_diff":
                home_form[5]["ppg"]
                - away_form[5]["ppg"],

            "win_rate_diff":
                home_form[5]["win_rate"]
                - away_form[5]["win_rate"],

            "goals_scored_diff":
                home_form[5]["goals_scored"]
                - away_form[5]["goals_scored"],

            "goals_conceded_diff":
                home_form[5]["goals_conceded"]
                - away_form[5]["goals_conceded"],

            "goal_difference_diff":
                home_form[5]["goal_difference"]
                - away_form[5]["goal_difference"],

            "shots_diff":
                home_form[5]["shots"]
                - away_form[5]["shots"],

            "shots_on_target_diff":
                home_form[5]["shots_on_target"]
                - away_form[5]["shots_on_target"],

            "corners_diff":
                home_form[5]["corners"]
                - away_form[5]["corners"],

            # Home/Away strength
            "home_home_win_rate":
                home_venue["win_rate"],
            "home_home_goals_avg":
                home_venue["goals_scored"],
            "home_home_conceded_avg":
                home_venue["goals_conceded"],
            "home_home_ppg":
                home_venue["ppg"],

            "away_away_win_rate":
                away_venue["win_rate"],
            "away_away_goals_avg":
                away_venue["goals_scored"],
            "away_away_conceded_avg":
                away_venue["goals_conceded"],
            "away_away_ppg":
                away_venue["ppg"],

            # Elo
            "home_elo": home_elo,
            "away_elo": away_elo,
            "elo_diff":
                home_elo - away_elo,

            # Rest
            "home_rest_days": home_rest,
            "away_rest_days": away_rest,
            "rest_days_diff":
                home_rest - away_rest,

            # Market
            "market_b365_home_prob": market_home,
            "market_b365_draw_prob": market_draw,
            "market_b365_away_prob": market_away,

            "market_avg_home_prob": market_home,
            "market_avg_draw_prob": market_draw,
            "market_avg_away_prob": market_away,

            "market_b365_margin": market_margin,
            "market_avg_margin": market_margin,
        }

        # ======================================================
        # V4 BALANCE FEATURES
        # ======================================================

        features["abs_elo_diff"] = abs(
            features["elo_diff"]
        )

        features["abs_form_points_diff"] = abs(
            features["form_points_diff"]
        )

        features["abs_ppg_diff"] = abs(
            features["ppg_diff"]
        )

        features["abs_ppg_diff_3"] = abs(
            features["home_ppg_3"]
            - features["away_ppg_3"]
        )

        features["abs_ppg_diff_5"] = abs(
            features["home_ppg_5"]
            - features["away_ppg_5"]
        )

        features["abs_ppg_diff_10"] = abs(
            features["home_ppg_10"]
            - features["away_ppg_10"]
        )

        features["abs_win_rate_diff"] = abs(
            features["win_rate_diff"]
        )

        features["abs_win_rate_diff_3"] = abs(
            features["home_win_rate_3"]
            - features["away_win_rate_3"]
        )

        features["abs_win_rate_diff_5"] = abs(
            features["home_win_rate_5"]
            - features["away_win_rate_5"]
        )

        features["abs_win_rate_diff_10"] = abs(
            features["home_win_rate_10"]
            - features["away_win_rate_10"]
        )

        features["abs_form_points_diff_3"] = abs(
            features["home_form_points_3"]
            - features["away_form_points_3"]
        )

        features["abs_form_points_diff_5"] = abs(
            features["home_form_points_5"]
            - features["away_form_points_5"]
        )

        features["abs_form_points_diff_10"] = abs(
            features["home_form_points_10"]
            - features["away_form_points_10"]
        )

        features["abs_goals_scored_diff_3"] = abs(
            features["home_goals_scored_3"]
            - features["away_goals_scored_3"]
        )

        features["abs_goals_scored_diff_5"] = abs(
            features["home_goals_scored_5"]
            - features["away_goals_scored_5"]
        )

        features["abs_goals_scored_diff_10"] = abs(
            features["home_goals_scored_10"]
            - features["away_goals_scored_10"]
        )

        features["abs_goals_conceded_diff_3"] = abs(
            features["home_goals_conceded_3"]
            - features["away_goals_conceded_3"]
        )

        features["abs_goals_conceded_diff_5"] = abs(
            features["home_goals_conceded_5"]
            - features["away_goals_conceded_5"]
        )

        features["abs_goals_conceded_diff_10"] = abs(
            features["home_goals_conceded_10"]
            - features["away_goals_conceded_10"]
        )

        features["abs_goal_difference_diff"] = abs(
            features["goal_difference_diff"]
        )

        features["abs_goal_diff_5"] = abs(
            features["home_goal_diff_5"]
            - features["away_goal_diff_5"]
        )

        features["abs_goal_diff_10"] = abs(
            features["home_goal_diff_10"]
            - features["away_goal_diff_10"]
        )

        features["abs_shots_diff"] = abs(
            features["shots_diff"]
        )

        features["abs_shots_on_target_diff"] = abs(
            features["shots_on_target_diff"]
        )

        features["abs_corners_diff"] = abs(
            features["corners_diff"]
        )

        features["abs_home_away_ppg_diff"] = abs(
            features["home_home_ppg"]
            - features["away_away_ppg"]
        )

        features["abs_home_away_win_rate_diff"] = abs(
            features["home_home_win_rate"]
            - features["away_away_win_rate"]
        )

        features["abs_home_away_goals_diff"] = abs(
            features["home_home_goals_avg"]
            - features["away_away_goals_avg"]
        )

        features["abs_home_away_conceded_diff"] = abs(
            features["home_home_conceded_avg"]
            - features["away_away_conceded_avg"]
        )

        return features