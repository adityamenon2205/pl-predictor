from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    BASE_DIR
    / "ml"
    / "data"
    / "processed"
    / "training_features_v4.csv"
)

MODEL_DIR = (
    BASE_DIR
    / "ml"
    / "models"
)

TEST_SEASON = "2025_26"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("V5 POISSON GOAL MODEL")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")


# ============================================================
# CREATE GOAL TARGETS
# ============================================================

"""
The existing V4 dataset contains FTR but not the actual
home/away goal columns.

Therefore, recover goals from the original football-data
CSV files.

This script expects the raw CSV files to be located in:

ml/data/raw/
"""


# ============================================================
# RAW DATA DISCOVERY
# ============================================================

RAW_DIR = (
    BASE_DIR
    / "ml"
    / "data"
    / "raw"
)

raw_files = sorted(
    RAW_DIR.glob("*.csv")
)

if not raw_files:

    raise FileNotFoundError(
        f"No raw CSV files found in {RAW_DIR}"
    )

print(
    f"\nFound {len(raw_files)} raw CSV files."
)


# ============================================================
# LOAD RAW MATCH RESULTS
# ============================================================

raw_matches = []

for file in raw_files:

    try:

        raw = pd.read_csv(
            file,
            encoding="latin1"
        )

    except Exception as e:  # noqa: BLE001

        print(
            f"Skipping {file.name}: {e}"
        )

        continue


    required = {
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG"
    }


    if not required.issubset(
        raw.columns
    ):

        print(
            f"Skipping {file.name}: "
            "required columns missing"
        )

        continue


    temp = raw[
        [
            "Date",
            "HomeTeam",
            "AwayTeam",
            "FTHG",
            "FTAG"
        ]
    ].copy()


    raw_matches.append(
        temp
    )


if not raw_matches:

    raise ValueError(
        "Could not load any valid "
        "football-data result files."
    )


raw_df = pd.concat(
    raw_matches,
    ignore_index=True
)


# ============================================================
# CLEAN RAW DATA
# ============================================================

# Raw football-data files use DD/MM/YY style dates.
raw_df["Date"] = pd.to_datetime(
    raw_df["Date"],
    dayfirst=True,
    errors="coerce"
)


# V4 dataset already uses YYYY-MM-DD.
df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)


# Normalize both to date only.
raw_df["Date"] = (
    raw_df["Date"]
    .dt.normalize()
)

df["Date"] = (
    df["Date"]
    .dt.normalize()
)


# Clean team names.
raw_df["HomeTeam"] = (
    raw_df["HomeTeam"]
    .astype(str)
    .str.strip()
)

raw_df["AwayTeam"] = (
    raw_df["AwayTeam"]
    .astype(str)
    .str.strip()
)

df["HomeTeam"] = (
    df["HomeTeam"]
    .astype(str)
    .str.strip()
)

df["AwayTeam"] = (
    df["AwayTeam"]
    .astype(str)
    .str.strip()
)


# Convert goals to numeric.
raw_df["FTHG"] = pd.to_numeric(
    raw_df["FTHG"],
    errors="coerce"
)

raw_df["FTAG"] = pd.to_numeric(
    raw_df["FTAG"],
    errors="coerce"
)


raw_df = raw_df.dropna(
    subset=[
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG"
    ]
)


# ============================================================
# REMOVE DUPLICATE MATCHES
# ============================================================

raw_df = raw_df.drop_duplicates(
    subset=[
        "Date",
        "HomeTeam",
        "AwayTeam"
    ],
    keep="first"
)


print(
    f"\nValid raw matches: "
    f"{len(raw_df)}"
)


# ============================================================
# MERGE GOALS
# ============================================================

print(
    "\nMerging actual goals into V4 dataset..."
)


df = df.merge(
    raw_df[
        [
            "Date",
            "HomeTeam",
            "AwayTeam",
            "FTHG",
            "FTAG"
        ]
    ],
    on=[
        "Date",
        "HomeTeam",
        "AwayTeam"
    ],
    how="left"
)


# ============================================================
# VALIDATE MERGE
# ============================================================

missing_goals = df[
    df["FTHG"].isna()
    | df["FTAG"].isna()
]


print(
    f"Matches missing goals: "
    f"{len(missing_goals)}"
)


if not missing_goals.empty:

    print(
        "\nFirst unmatched matches:"
    )

    print(
        missing_goals[
            [
                "Date",
                "Season",
                "HomeTeam",
                "AwayTeam"
            ]
        ].head(20).to_string(
            index=False
        )
    )


# ============================================================
# STRICT VALIDATION
# ============================================================

if len(missing_goals) > 0:

    raise ValueError(
        f"{len(missing_goals)} matches could "
        "not be matched with raw goal data. "
        "Stop here and inspect the unmatched "
        "team/date combinations."
    )


print(
    "\nSUCCESS: All matches have "
    "valid goal values."
)

# ============================================================
# VALIDATE GOALS
# ============================================================

missing_goals = df[
    df["FTHG"].isna()
    | df["FTAG"].isna()
]


if not missing_goals.empty:

    print(
        f"\nWARNING: "
        f"{len(missing_goals)} matches "
        "are missing goal values."
    )

    print(
        missing_goals[
            [
                "Date",
                "Season",
                "HomeTeam",
                "AwayTeam"
            ]
        ].head(20)
    )


df = df.dropna(
    subset=[
        "FTHG",
        "FTAG"
    ]
)


print(
    f"\nMatches with valid goals: "
    f"{len(df)}"
)


# ============================================================
# IMPORTANT:
# REMOVE CURRENT TEST SEASON FROM TRAINING
# ============================================================

train_df = df[
    df["Season"] != TEST_SEASON
].copy()


test_df = df[
    df["Season"] == TEST_SEASON
].copy()


print(
    f"\nTraining matches: "
    f"{len(train_df)}"
)

print(
    f"Test matches: "
    f"{len(test_df)}"
)


# ============================================================
# FEATURES
# ============================================================

excluded_columns = {
    "Date",
    "Season",
    "HomeTeam",
    "AwayTeam",
    "FTR",
    "FTHG",
    "FTAG"
}


feature_columns = [
    column
    for column in df.columns
    if column not in excluded_columns
]


print(
    f"\nNumber of features: "
    f"{len(feature_columns)}"
)


# ============================================================
# PREPARE X / Y
# ============================================================

X_train = train_df[
    feature_columns
]

X_test = test_df[
    feature_columns
]


y_home_train = (
    train_df["FTHG"]
    .astype(float)
)

y_away_train = (
    train_df["FTAG"]
    .astype(float)
)


y_home_test = (
    test_df["FTHG"]
    .astype(float)
)

y_away_test = (
    test_df["FTAG"]
    .astype(float)
)


# ============================================================
# HOME GOALS MODEL
# ============================================================

print(
    "\nTraining Home Goals model..."
)


home_model = RandomForestRegressor(
    n_estimators=500,
    max_depth=None,
    min_samples_split=4,
    min_samples_leaf=2,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1
)


home_model.fit(
    X_train,
    y_home_train
)


# ============================================================
# AWAY GOALS MODEL
# ============================================================

print(
    "Training Away Goals model..."
)


away_model = RandomForestRegressor(
    n_estimators=500,
    max_depth=None,
    min_samples_split=4,
    min_samples_leaf=2,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1
)


away_model.fit(
    X_train,
    y_away_train
)


# ============================================================
# EVALUATE GOAL MODELS
# ============================================================

home_pred = home_model.predict(
    X_test
)

away_pred = away_model.predict(
    X_test
)


home_mae = mean_absolute_error(
    y_home_test,
    home_pred
)

away_mae = mean_absolute_error(
    y_away_test,
    away_pred
)


home_rmse = np.sqrt(
    mean_squared_error(
        y_home_test,
        home_pred
    )
)

away_rmse = np.sqrt(
    mean_squared_error(
        y_away_test,
        away_pred
    )
)


print("\n" + "=" * 70)
print("GOAL MODEL PERFORMANCE")
print("=" * 70)


print(
    f"\nHome Goals MAE : "
    f"{home_mae:.4f}"
)

print(
    f"Home Goals RMSE: "
    f"{home_rmse:.4f}"
)

print(
    f"Away Goals MAE : "
    f"{away_mae:.4f}"
)

print(
    f"Away Goals RMSE: "
    f"{away_rmse:.4f}"
)


# ============================================================
# SAVE MODELS
# ============================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


home_bundle = {
    "model": home_model,
    "features": feature_columns
}


away_bundle = {
    "model": away_model,
    "features": feature_columns
}


home_path = (
    MODEL_DIR
    / "poisson_v5_home_goals.pkl"
)

away_path = (
    MODEL_DIR
    / "poisson_v5_away_goals.pkl"
)


joblib.dump(
    home_bundle,
    home_path
)

joblib.dump(
    away_bundle,
    away_path
)


print(
    "\nModels saved:"
)

print(
    f"  {home_path}"
)

print(
    f"  {away_path}"
)


# ============================================================
# SAVE GOAL PREDICTIONS
# ============================================================

goal_predictions = test_df[
    [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG"
    ]
].copy()


goal_predictions[
    "Pred_Home_Goals"
] = home_pred

goal_predictions[
    "Pred_Away_Goals"
] = away_pred


goal_predictions.to_csv(
    MODEL_DIR
    / "poisson_v5_goal_predictions.csv",
    index=False
)


print(
    "\nGoal predictions saved."
)


print("\n" + "=" * 70)
print("V5 GOAL MODEL TRAINING COMPLETE")
print("=" * 70)