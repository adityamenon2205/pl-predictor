from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    BASE_DIR
    / "ml"
    / "data"
    / "processed"
    / "training_features_v3.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "ml"
    / "data"
    / "processed"
    / "training_features_v4.csv"
)


# ============================================================
# LOAD V3 DATA
# ============================================================

print("=" * 70)
print("CREATING TRAINING FEATURES V4")
print("=" * 70)

print("\nLoading V3 dataset...")

df = pd.read_csv(INPUT_PATH)

print(f"V3 shape: {df.shape}")


# ============================================================
# REQUIRED V3 FEATURES
# ============================================================

required_columns = [
    # Form
    "home_form_points_3",
    "away_form_points_3",
    "home_form_points_5",
    "away_form_points_5",
    "home_form_points_10",
    "away_form_points_10",

    # PPG
    "home_ppg_3",
    "away_ppg_3",
    "home_ppg_5",
    "away_ppg_5",
    "home_ppg_10",
    "away_ppg_10",

    # Win rate
    "home_win_rate_3",
    "away_win_rate_3",
    "home_win_rate_5",
    "away_win_rate_5",
    "home_win_rate_10",
    "away_win_rate_10",

    # Goals scored
    "home_goals_scored_3",
    "away_goals_scored_3",
    "home_goals_scored_5",
    "away_goals_scored_5",
    "home_goals_scored_10",
    "away_goals_scored_10",

    # Goals conceded
    "home_goals_conceded_3",
    "away_goals_conceded_3",
    "home_goals_conceded_5",
    "away_goals_conceded_5",
    "home_goals_conceded_10",
    "away_goals_conceded_10",

    # Goal difference
    "home_goal_diff_5",
    "away_goal_diff_5",
    "home_goal_diff_10",
    "away_goal_diff_10",

    # Overall attacking statistics
    "home_shots_avg",
    "away_shots_avg",
    "home_shots_on_target_avg",
    "away_shots_on_target_avg",
    "home_corners_avg",
    "away_corners_avg",

    # Existing differences
    "form_points_diff",
    "ppg_diff",
    "win_rate_diff",
    "goals_scored_diff",
    "goals_conceded_diff",
    "goal_difference_diff",
    "shots_diff",
    "shots_on_target_diff",
    "corners_diff",

    # Home/away splits
    "home_home_win_rate",
    "away_away_win_rate",
    "home_home_goals_avg",
    "away_away_goals_avg",
    "home_home_conceded_avg",
    "away_away_conceded_avg",
    "home_home_ppg",
    "away_away_ppg",

    # Elo
    "home_elo",
    "away_elo",
    "elo_diff",

    # Rest
    "home_rest_days",
    "away_rest_days",
    "rest_days_diff",

    # Market
    "market_b365_home_prob",
    "market_b365_draw_prob",
    "market_b365_away_prob",
    "market_avg_home_prob",
    "market_avg_draw_prob",
    "market_avg_away_prob",
    "market_b365_margin",
    "market_avg_margin",
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("\nERROR: Required columns are missing:")

    for column in missing_columns:
        print(f"  - {column}")

    raise ValueError(
        "V3 dataset does not contain all required columns."
    )

print(
    f"\n✓ All {len(required_columns)} required "
    "V3 features are present."
)


# ============================================================
# CREATE MATCH-BALANCE FEATURES
# ============================================================

print("\nCreating V4 match-balance features...")


# ------------------------------------------------------------
# 1. ELO BALANCE
# ------------------------------------------------------------

df["abs_elo_diff"] = (
    df["elo_diff"].abs()
)


# ------------------------------------------------------------
# 2. FORM BALANCE
# ------------------------------------------------------------

df["abs_form_points_diff"] = (
    df["form_points_diff"].abs()
)


# ------------------------------------------------------------
# 3. PPG BALANCE
# ------------------------------------------------------------

df["abs_ppg_diff"] = (
    df["ppg_diff"].abs()
)

df["abs_ppg_diff_3"] = (
    (
        df["home_ppg_3"]
        - df["away_ppg_3"]
    ).abs()
)

df["abs_ppg_diff_5"] = (
    (
        df["home_ppg_5"]
        - df["away_ppg_5"]
    ).abs()
)

df["abs_ppg_diff_10"] = (
    (
        df["home_ppg_10"]
        - df["away_ppg_10"]
    ).abs()
)


# ------------------------------------------------------------
# 4. WIN-RATE BALANCE
# ------------------------------------------------------------

df["abs_win_rate_diff"] = (
    df["win_rate_diff"].abs()
)

df["abs_win_rate_diff_3"] = (
    (
        df["home_win_rate_3"]
        - df["away_win_rate_3"]
    ).abs()
)

df["abs_win_rate_diff_5"] = (
    (
        df["home_win_rate_5"]
        - df["away_win_rate_5"]
    ).abs()
)

df["abs_win_rate_diff_10"] = (
    (
        df["home_win_rate_10"]
        - df["away_win_rate_10"]
    ).abs()
)


# ------------------------------------------------------------
# 5. FORM-WINDOW BALANCE
# ------------------------------------------------------------

df["abs_form_points_diff_3"] = (
    (
        df["home_form_points_3"]
        - df["away_form_points_3"]
    ).abs()
)

df["abs_form_points_diff_5"] = (
    (
        df["home_form_points_5"]
        - df["away_form_points_5"]
    ).abs()
)

df["abs_form_points_diff_10"] = (
    (
        df["home_form_points_10"]
        - df["away_form_points_10"]
    ).abs()
)


# ------------------------------------------------------------
# 6. GOALS SCORED BALANCE
# ------------------------------------------------------------

df["abs_goals_scored_diff_3"] = (
    (
        df["home_goals_scored_3"]
        - df["away_goals_scored_3"]
    ).abs()
)

df["abs_goals_scored_diff_5"] = (
    (
        df["home_goals_scored_5"]
        - df["away_goals_scored_5"]
    ).abs()
)

df["abs_goals_scored_diff_10"] = (
    (
        df["home_goals_scored_10"]
        - df["away_goals_scored_10"]
    ).abs()
)


# ------------------------------------------------------------
# 7. GOALS CONCEDED BALANCE
# ------------------------------------------------------------

df["abs_goals_conceded_diff_3"] = (
    (
        df["home_goals_conceded_3"]
        - df["away_goals_conceded_3"]
    ).abs()
)

df["abs_goals_conceded_diff_5"] = (
    (
        df["home_goals_conceded_5"]
        - df["away_goals_conceded_5"]
    ).abs()
)

df["abs_goals_conceded_diff_10"] = (
    (
        df["home_goals_conceded_10"]
        - df["away_goals_conceded_10"]
    ).abs()
)


# ------------------------------------------------------------
# 8. GOAL-DIFFERENCE BALANCE
# ------------------------------------------------------------

df["abs_goal_difference_diff"] = (
    df["goal_difference_diff"].abs()
)

df["abs_goal_diff_5"] = (
    (
        df["home_goal_diff_5"]
        - df["away_goal_diff_5"]
    ).abs()
)

df["abs_goal_diff_10"] = (
    (
        df["home_goal_diff_10"]
        - df["away_goal_diff_10"]
    ).abs()
)


# ------------------------------------------------------------
# 9. SHOTS BALANCE
# ------------------------------------------------------------

df["abs_shots_diff"] = (
    df["shots_diff"].abs()
)


# ------------------------------------------------------------
# 10. SHOTS-ON-TARGET BALANCE
# ------------------------------------------------------------

df["abs_shots_on_target_diff"] = (
    df["shots_on_target_diff"].abs()
)


# ------------------------------------------------------------
# 11. CORNERS BALANCE
# ------------------------------------------------------------

df["abs_corners_diff"] = (
    df["corners_diff"].abs()
)


# ------------------------------------------------------------
# 12. HOME/AWAY STRENGTH BALANCE
# ------------------------------------------------------------

df["abs_home_away_ppg_diff"] = (
    (
        df["home_home_ppg"]
        - df["away_away_ppg"]
    ).abs()
)

df["abs_home_away_win_rate_diff"] = (
    (
        df["home_home_win_rate"]
        - df["away_away_win_rate"]
    ).abs()
)

df["abs_home_away_goals_diff"] = (
    (
        df["home_home_goals_avg"]
        - df["away_away_goals_avg"]
    ).abs()
)

df["abs_home_away_conceded_diff"] = (
    (
        df["home_home_conceded_avg"]
        - df["away_away_conceded_avg"]
    ).abs()
)


# ============================================================
# LIST NEW FEATURES
# ============================================================

new_features = [
    "abs_elo_diff",

    "abs_form_points_diff",

    "abs_ppg_diff",
    "abs_ppg_diff_3",
    "abs_ppg_diff_5",
    "abs_ppg_diff_10",

    "abs_win_rate_diff",
    "abs_win_rate_diff_3",
    "abs_win_rate_diff_5",
    "abs_win_rate_diff_10",

    "abs_form_points_diff_3",
    "abs_form_points_diff_5",
    "abs_form_points_diff_10",

    "abs_goals_scored_diff_3",
    "abs_goals_scored_diff_5",
    "abs_goals_scored_diff_10",

    "abs_goals_conceded_diff_3",
    "abs_goals_conceded_diff_5",
    "abs_goals_conceded_diff_10",

    "abs_goal_difference_diff",
    "abs_goal_diff_5",
    "abs_goal_diff_10",

    "abs_shots_diff",
    "abs_shots_on_target_diff",
    "abs_corners_diff",

    "abs_home_away_ppg_diff",
    "abs_home_away_win_rate_diff",
    "abs_home_away_goals_diff",
    "abs_home_away_conceded_diff",
]


# ============================================================
# CHECK NEW FEATURES
# ============================================================

print(
    f"\n✓ Added {len(new_features)} "
    "new V4 balance features."
)

print("\nNew features:")

for feature in new_features:
    print(f"  - {feature}")


# ============================================================
# MISSING VALUE CHECK
# ============================================================

print("\nChecking for missing values...")

missing_counts = (
    df[new_features]
    .isna()
    .sum()
)

missing_features = (
    missing_counts[
        missing_counts > 0
    ]
)

if not missing_features.empty:

    print(
        "\nERROR: Missing values found:"
    )

    print(
        missing_features
    )

    raise ValueError(
        "V4 contains missing values."
    )

else:

    print(
        "✓ No missing values "
        "in new features."
    )


# ============================================================
# INFINITE VALUE CHECK
# ============================================================

print(
    "\nChecking for infinite values..."
)

numeric_values = (
    df[new_features]
    .select_dtypes(
        include=[np.number]
    )
)

if np.isinf(
    numeric_values.values
).any():

    raise ValueError(
        "Infinite values detected "
        "in V4 features."
    )

else:

    print(
        "✓ No infinite values "
        "in new features."
    )


# ============================================================
# DATASET SIZE
# ============================================================

print("\n" + "=" * 70)
print("V4 DATASET INFORMATION")
print("=" * 70)

print(
    f"\nRows: {len(df)}"
)

print(
    f"Columns: {len(df.columns)}"
)

print(
    f"V3 columns: "
    f"{len(df.columns) - len(new_features)}"
)

print(
    f"New V4 features: "
    f"{len(new_features)}"
)


# ============================================================
# SEASON DISTRIBUTION
# ============================================================

print("\nSeason distribution:")

season_counts = (
    df["Season"]
    .value_counts()
    .sort_index()
)

print(
    season_counts.to_string()
)


# ============================================================
# VERIFY 2026/27 IS NOT INCLUDED
# ============================================================

if "2026_27" in df["Season"].values:

    print(
        "\nWARNING: 2026/27 data is present!"
    )

    print(
        "Do NOT train V4 until this is removed."
    )

else:

    print(
        "\n✓ 2026/27 is not present."
    )


# ============================================================
# TARGET DISTRIBUTION
# ============================================================

print("\nTarget distribution:")

target_counts = (
    df["FTR"]
    .value_counts()
    .reindex(
        ["H", "D", "A"]
    )
)

print(
    target_counts.to_string()
)


# ============================================================
# SAVE V4
# ============================================================

print("\nSaving V4 dataset...")

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_PATH,
    index=False
)

print(
    "\n✓ V4 dataset saved:"
)

print(
    f"  {OUTPUT_PATH}"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("V4 FEATURE ENGINEERING COMPLETE")
print("=" * 70)

print(
    f"""
V3:
    Rows    : 6080
    Columns : 76

V4:
    Rows    : {len(df)}
    Columns : {len(df.columns)}

New balance features:
    {len(new_features)}

Missing values:
    0

Infinite values:
    0

2026/27 included:
    {"YES - CHECK DATASET" if "2026_27" in df["Season"].values else "NO"}

Output:
    {OUTPUT_PATH}
"""
)

print("=" * 70)