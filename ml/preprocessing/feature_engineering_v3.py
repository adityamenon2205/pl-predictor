from collections import defaultdict, deque
from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = Path("ml/data/processed/epl_matches.csv")
OUTPUT_FILE = Path("ml/data/processed/training_features_v3.csv")

INITIAL_ELO = 1500
ELO_K = 20
HOME_ELO_ADVANTAGE = 60

FORM_WINDOWS = [3, 5, 10]

# --------------------------------------------------
# Bookmaker Market Features
# --------------------------------------------------


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_average(values):
    return np.mean(values) if values else 0.0


def get_form_stats(history, window):

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
        "ppg": safe_average(points),
        "win_rate": sum(x["points"] == 3 for x in recent) / len(recent),
        "goals_scored": safe_average(
            [x["goals_scored"] for x in recent]
        ),
        "goals_conceded": safe_average(
            [x["goals_conceded"] for x in recent]
        ),
        "goal_difference": safe_average(
            [
                x["goals_scored"] - x["goals_conceded"]
                for x in recent
            ]
        ),
        "shots": safe_average(
            [x["shots"] for x in recent]
        ),
        "shots_on_target": safe_average(
            [x["shots_on_target"] for x in recent]
        ),
        "corners": safe_average(
            [x["corners"] for x in recent]
        ),
    }


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

        "goals_scored": safe_average(
            [x["goals_scored"] for x in history]
        ),

        "goals_conceded": safe_average(
            [x["goals_conceded"] for x in history]
        ),

        "ppg": safe_average(
            [x["points"] for x in history]
        ),
    }


def elo_expected(elo_home, elo_away):

    difference = (
        elo_away
        - (elo_home + HOME_ELO_ADVANTAGE)
    ) / 400

    return 1 / (1 + 10 ** difference)


def update_elo(home_elo, away_elo, result):

    expected_home = elo_expected(
        home_elo,
        away_elo
    )

    if result == "H":
        actual_home = 1.0
    elif result == "D":
        actual_home = 0.5
    else:
        actual_home = 0.0

    change = ELO_K * (
        actual_home - expected_home
    )

    return (
        home_elo + change,
        away_elo - change
    )


# ============================================================
# BOOKMAKER FEATURES
# ============================================================

def calculate_market_features(match):

    """
    Convert bookmaker decimal odds into normalized
    implied probabilities.

    Uses Bet365 and average market odds.
    """

    # --------------------------------------------------------
    # Bet365 probabilities
    # --------------------------------------------------------

    b365_home = match.get("B365H", np.nan)
    b365_draw = match.get("B365D", np.nan)
    b365_away = match.get("B365A", np.nan)

    if (
        pd.notna(b365_home)
        and pd.notna(b365_draw)
        and pd.notna(b365_away)
        and b365_home > 0
        and b365_draw > 0
        and b365_away > 0
    ):

        b365_raw = np.array([
            1 / b365_home,
            1 / b365_draw,
            1 / b365_away,
        ])

        b365_margin = b365_raw.sum()

        b365_probs = (
            b365_raw / b365_margin
        )

    else:

        b365_probs = np.array([
            np.nan,
            np.nan,
            np.nan,
        ])

        b365_margin = np.nan

    # --------------------------------------------------------
    # Average market probabilities
    # --------------------------------------------------------

    avg_home = match.get("AvgH", np.nan)
    avg_draw = match.get("AvgD", np.nan)
    avg_away = match.get("AvgA", np.nan)

    if (
        pd.notna(avg_home)
        and pd.notna(avg_draw)
        and pd.notna(avg_away)
        and avg_home > 0
        and avg_draw > 0
        and avg_away > 0
    ):

        avg_raw = np.array([
            1 / avg_home,
            1 / avg_draw,
            1 / avg_away,
        ])

        avg_margin = avg_raw.sum()

        avg_probs = (
            avg_raw / avg_margin
        )

    else:
        # Avg bookmaker odds are unavailable.
        # Fall back to Bet365 probabilities.
        avg_probs = b365_probs.copy()
        avg_margin = b365_margin

    # --------------------------------------------------------
    # Market favorite
    # --------------------------------------------------------

    favorite_index = np.argmax(avg_probs)

    if favorite_index == 0:
        favorite = "H"
    elif favorite_index == 1:
        favorite = "D"
    else:
        favorite = "A"

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "market_b365_home_prob": b365_probs[0],
        "market_b365_draw_prob": b365_probs[1],
        "market_b365_away_prob": b365_probs[2],

        "market_avg_home_prob": avg_probs[0],
        "market_avg_draw_prob": avg_probs[1],
        "market_avg_away_prob": avg_probs[2],

        "market_b365_margin": b365_margin,
        "market_avg_margin": avg_margin,

        "market_favorite": favorite,

    }


# ============================================================
# MAIN
# ============================================================

def main():

    print("Loading processed EPL dataset...")

    df = pd.read_csv(INPUT_FILE)

    df["Date"] = pd.to_datetime(
        df["Date"]
    )

    # --------------------------------------------------------
    # Chronological ordering
    # --------------------------------------------------------

    df = df.sort_values(
        ["Date", "Season"]
    ).reset_index(drop=True)

    print(f"Loaded {len(df)} matches.")

    print(
        "Building Feature Engineering V3..."
    )

    print(
        "V3 includes V2 features + bookmaker market features."
    )

    print()

    # --------------------------------------------------------
    # Team state
    # --------------------------------------------------------

    team_history = defaultdict(
        lambda: deque(maxlen=10)
    )

    home_history = defaultdict(list)

    away_history = defaultdict(list)

    elo = defaultdict(
        lambda: INITIAL_ELO
    )

    last_match_date = {}

    feature_rows = []

    # --------------------------------------------------------
    # Process matches chronologically
    # --------------------------------------------------------

    for _, match in df.iterrows():

        date = match["Date"]

        home = match["HomeTeam"]

        away = match["AwayTeam"]

        # ====================================================
        # CURRENT ELO
        # ====================================================

        home_elo = elo[home]

        away_elo = elo[away]

        # ====================================================
        # FORM
        # ====================================================

        home_form = {
            window: get_form_stats(
                team_history[home],
                window
            )
            for window in FORM_WINDOWS
        }

        away_form = {
            window: get_form_stats(
                team_history[away],
                window
            )
            for window in FORM_WINDOWS
        }

        # ====================================================
        # VENUE STATS
        # ====================================================

        home_venue = get_venue_stats(
            home_history[home]
        )

        away_venue = get_venue_stats(
            away_history[away]
        )

        # ====================================================
        # REST DAYS
        # ====================================================

        if home in last_match_date:

            home_rest_days = (
                date - last_match_date[home]
            ).days

        else:

            home_rest_days = 0

        if away in last_match_date:

            away_rest_days = (
                date - last_match_date[away]
            ).days

        else:

            away_rest_days = 0

        # ====================================================
        # MARKET FEATURES
        # ====================================================

        market = calculate_market_features(
            match
        )

        # ====================================================
        # FEATURE ROW
        # ====================================================

        row = {

            # ------------------------------------------------
            # Metadata
            # ------------------------------------------------

            "Date": date,
            "Season": match["Season"],
            "HomeTeam": home,
            "AwayTeam": away,

            # ------------------------------------------------
            # Target
            # ------------------------------------------------

            "FTR": match["FTR"],

            # ------------------------------------------------
            # HOME FORM
            # ------------------------------------------------

            "home_form_points_3":
                home_form[3]["points"],

            "home_form_points_5":
                home_form[5]["points"],

            "home_form_points_10":
                home_form[10]["points"],

            "home_ppg_3":
                home_form[3]["ppg"],

            "home_ppg_5":
                home_form[5]["ppg"],

            "home_ppg_10":
                home_form[10]["ppg"],

            "home_win_rate_3":
                home_form[3]["win_rate"],

            "home_win_rate_5":
                home_form[5]["win_rate"],

            "home_win_rate_10":
                home_form[10]["win_rate"],

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

            # ------------------------------------------------
            # AWAY FORM
            # ------------------------------------------------

            "away_form_points_3":
                away_form[3]["points"],

            "away_form_points_5":
                away_form[5]["points"],

            "away_form_points_10":
                away_form[10]["points"],

            "away_ppg_3":
                away_form[3]["ppg"],

            "away_ppg_5":
                away_form[5]["ppg"],

            "away_ppg_10":
                away_form[10]["ppg"],

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

            # ------------------------------------------------
            # DIFFERENCE FEATURES
            # ------------------------------------------------

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

            # ------------------------------------------------
            # HOME / AWAY STRENGTH
            # ------------------------------------------------

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

            # ------------------------------------------------
            # ELO
            # ------------------------------------------------

            "home_elo": home_elo,

            "away_elo": away_elo,

            "elo_diff":
                home_elo - away_elo,

            # ------------------------------------------------
            # REST
            # ------------------------------------------------

            "home_rest_days":
                home_rest_days,

            "away_rest_days":
                away_rest_days,

            "rest_days_diff":
                home_rest_days - away_rest_days,

            # ------------------------------------------------
            # MARKET FEATURES
            # ------------------------------------------------

            "market_b365_home_prob":
                market["market_b365_home_prob"],

            "market_b365_draw_prob":
                market["market_b365_draw_prob"],

            "market_b365_away_prob":
                market["market_b365_away_prob"],

            "market_avg_home_prob":
                market["market_avg_home_prob"],

            "market_avg_draw_prob":
                market["market_avg_draw_prob"],

            "market_avg_away_prob":
                market["market_avg_away_prob"],

            "market_b365_margin":
                market["market_b365_margin"],

            "market_avg_margin":
                market["market_avg_margin"],
        }

        feature_rows.append(row)

        # ====================================================
        # UPDATE TEAM HISTORY
        # ====================================================

        if match["FTR"] == "H":

            home_points = 3
            away_points = 0

        elif match["FTR"] == "D":

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

        team_history[home].append(
            home_record
        )

        team_history[away].append(
            away_record
        )

        home_history[home].append(
            home_record
        )

        away_history[away].append(
            away_record
        )

        # ====================================================
        # UPDATE ELO
        # ====================================================

        new_home_elo, new_away_elo = update_elo(
            home_elo,
            away_elo,
            match["FTR"]
        )

        elo[home] = new_home_elo

        elo[away] = new_away_elo

        # ====================================================
        # UPDATE LAST MATCH DATE
        # ====================================================

        last_match_date[home] = date

        last_match_date[away] = date

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    features_df = pd.DataFrame(
        feature_rows
    )

    features_df = features_df.sort_values(
        "Date"
    ).reset_index(drop=True)

    # ========================================================
    # VALIDATION
    # ========================================================

    print()
    print("Validating V3 dataset...")

    print(
        f"Rows generated: {len(features_df)}"
    )

    print(
        f"Columns generated: "
        f"{len(features_df.columns)}"
    )

    print(
        f"Missing values: "
        f"{features_df.isna().sum().sum()}"
    )

    print(
        f"Date range: "
        f"{features_df['Date'].min().date()} "
        f"to "
        f"{features_df['Date'].max().date()}"
    )

    print("\nMarket feature missing values:")

    market_columns = [
        "market_b365_home_prob",
        "market_b365_draw_prob",
        "market_b365_away_prob",
        "market_avg_home_prob",
        "market_avg_draw_prob",
        "market_avg_away_prob",
        "market_b365_margin",
        "market_avg_margin",
    ]

    print(features_df[market_columns].isna().sum())

    print("\nMarket probability statistics:")

    print(
        features_df[
            [
                "market_avg_home_prob",
                "market_avg_draw_prob",
                "market_avg_away_prob",
            ]
        ].describe()
    )

    print()

    print("Target distribution:")

    print(
        features_df["FTR"].value_counts()
    )

    print()

    print("Market feature sample:")

    print(
        features_df[
            [
                "HomeTeam",
                "AwayTeam",
                "market_avg_home_prob",
                "market_avg_draw_prob",
                "market_avg_away_prob",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    # ========================================================
    # SAVE
    # ========================================================

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    features_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()

    print(
        "Feature Engineering V3 complete."
    )

    print(
        f"Dataset saved to:\n"
        f"{OUTPUT_FILE.resolve()}"
    )


if __name__ == "__main__":
    main()