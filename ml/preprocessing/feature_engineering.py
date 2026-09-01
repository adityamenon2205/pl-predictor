from collections import defaultdict, deque
from pathlib import Path

import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "epl_matches.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "training_features.csv"
)


# --------------------------------------------------
# Configuration
# --------------------------------------------------

WINDOW = 5


# --------------------------------------------------
# Team history
# --------------------------------------------------

def create_team_state():
    """Create empty historical state for a team."""

    return {
        "results": deque(maxlen=WINDOW),
        "goals_for": deque(maxlen=WINDOW),
        "goals_against": deque(maxlen=WINDOW),
        "shots": deque(maxlen=WINDOW),
        "shots_on_target": deque(maxlen=WINDOW),
        "corners": deque(maxlen=WINDOW),

        "home_results": deque(maxlen=WINDOW),
        "home_goals_for": deque(maxlen=WINDOW),
        "home_goals_against": deque(maxlen=WINDOW),

        "away_results": deque(maxlen=WINDOW),
        "away_goals_for": deque(maxlen=WINDOW),
        "away_goals_against": deque(maxlen=WINDOW),
    }


# --------------------------------------------------
# Utility functions
# --------------------------------------------------

def average(values):
    """Return average of values, or 0 if empty."""

    if not values:
        return 0.0

    return sum(values) / len(values)


def win_rate(results):
    """Calculate win percentage."""

    if not results:
        return 0.0

    return sum(result == 3 for result in results) / len(results)


def points(results):
    """Calculate total points."""

    return sum(results)


# --------------------------------------------------
# Extract team features
# --------------------------------------------------

def get_team_features(state, prefix):
    """
    Convert a team's historical state into ML features.
    """

    features = {}

    # Overall recent form
    results = state["results"]

    features[f"{prefix}_form_points"] = points(results)
    features[f"{prefix}_win_rate"] = win_rate(results)

    features[f"{prefix}_goals_scored_avg"] = average(
        state["goals_for"]
    )

    features[f"{prefix}_goals_conceded_avg"] = average(
        state["goals_against"]
    )

    features[f"{prefix}_shots_avg"] = average(
        state["shots"]
    )

    features[f"{prefix}_shots_on_target_avg"] = average(
        state["shots_on_target"]
    )

    features[f"{prefix}_corners_avg"] = average(
        state["corners"]
    )

    # Home / away specific performance
    if prefix == "home":

        features["home_home_win_rate"] = win_rate(
            state["home_results"]
        )

        features["home_home_goals_avg"] = average(
            state["home_goals_for"]
        )

        features["home_home_conceded_avg"] = average(
            state["home_goals_against"]
        )

    elif prefix == "away":

        features["away_away_win_rate"] = win_rate(
            state["away_results"]
        )

        features["away_away_goals_avg"] = average(
            state["away_goals_for"]
        )

        features["away_away_conceded_avg"] = average(
            state["away_goals_against"]
        )

    return features


# --------------------------------------------------
# Update team state after a match
# --------------------------------------------------

def update_team_state(
    state,
    goals_for,
    goals_against,
    shots,
    shots_on_target,
    corners,
    result,
    venue
):
    """Update historical statistics after a match."""

    state["results"].append(result)

    state["goals_for"].append(goals_for)
    state["goals_against"].append(goals_against)

    state["shots"].append(shots)
    state["shots_on_target"].append(shots_on_target)
    state["corners"].append(corners)

    if venue == "home":

        state["home_results"].append(result)
        state["home_goals_for"].append(goals_for)
        state["home_goals_against"].append(goals_against)

    else:

        state["away_results"].append(result)
        state["away_goals_for"].append(goals_for)
        state["away_goals_against"].append(goals_against)


# --------------------------------------------------
# Create features
# --------------------------------------------------

def build_features(df):
    """
    Build leakage-safe pre-match features.
    """

    # Ensure chronological order
    df = df.sort_values(
        "Date"
    ).reset_index(drop=True)

    # Team states
    team_states = defaultdict(create_team_state)

    feature_rows = []

    for _, match in df.iterrows():

        home_team = match["HomeTeam"]
        away_team = match["AwayTeam"]

        home_state = team_states[home_team]
        away_state = team_states[away_team]

        # ------------------------------------------
        # Generate features BEFORE updating state
        # ------------------------------------------

        features = {
            "Date": match["Date"],
            "Season": match["Season"],
            "HomeTeam": home_team,
            "AwayTeam": away_team,
            "FTR": match["FTR"],
        }

        # Home team features
        features.update(
            get_team_features(
                home_state,
                "home"
            )
        )

        # Away team features
        features.update(
            get_team_features(
                away_state,
                "away"
            )
        )

        # ------------------------------------------
        # Difference features
        # ------------------------------------------

        features["form_points_diff"] = (
            features["home_form_points"]
            - features["away_form_points"]
        )

        features["win_rate_diff"] = (
            features["home_win_rate"]
            - features["away_win_rate"]
        )

        features["goals_scored_diff"] = (
            features["home_goals_scored_avg"]
            - features["away_goals_scored_avg"]
        )

        features["goals_conceded_diff"] = (
            features["home_goals_conceded_avg"]
            - features["away_goals_conceded_avg"]
        )

        features["shots_diff"] = (
            features["home_shots_avg"]
            - features["away_shots_avg"]
        )

        features["shots_on_target_diff"] = (
            features["home_shots_on_target_avg"]
            - features["away_shots_on_target_avg"]
        )

        features["corners_diff"] = (
            features["home_corners_avg"]
            - features["away_corners_avg"]
        )

        feature_rows.append(features)

        # ------------------------------------------
        # Update state AFTER generating features
        # ------------------------------------------

        home_goals = match["FTHG"]
        away_goals = match["FTAG"]

        # Home result
        if home_goals > away_goals:
            home_result = 3
            away_result = 0

        elif home_goals == away_goals:
            home_result = 1
            away_result = 1

        else:
            home_result = 0
            away_result = 3

        # Home team update
        update_team_state(
            home_state,
            goals_for=home_goals,
            goals_against=away_goals,
            shots=match["HS"],
            shots_on_target=match["HST"],
            corners=match["HC"],
            result=home_result,
            venue="home",
        )

        # Away team update
        update_team_state(
            away_state,
            goals_for=away_goals,
            goals_against=home_goals,
            shots=match["AS"],
            shots_on_target=match["AST"],
            corners=match["AC"],
            result=away_result,
            venue="away",
        )

    return pd.DataFrame(feature_rows)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("Loading processed EPL dataset...")

    df = pd.read_csv(
        INPUT_FILE,
        parse_dates=["Date"]
    )

    print(
        f"Loaded {len(df)} matches."
    )

    print("Building leakage-safe features...")

    feature_df = build_features(df)

    # Save
    feature_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nFeature dataset saved to:"
        f"\n{OUTPUT_FILE}"
    )

    print(
        f"\nShape: {feature_df.shape}"
    )

    print("\nFeature columns:")

    for column in feature_df.columns:
        print(f"  - {column}")


if __name__ == "__main__":
    main()