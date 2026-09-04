from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import poisson
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
)

# ============================================================
# CONFIGURATION
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

HOME_MODEL_PATH = (
    MODEL_DIR
    / "poisson_v5_home_goals.pkl"
)

AWAY_MODEL_PATH = (
    MODEL_DIR
    / "poisson_v5_away_goals.pkl"
)

TEST_SEASON = "2025_26"

MAX_GOALS = 10

OUTPUT_PATH = (
    MODEL_DIR
    / "poisson_v5_match_probabilities.csv"
)

COMPARISON_PATH = (
    MODEL_DIR
    / "poisson_v5_comparison.csv"
)


# ============================================================
# LABEL MAPPING
# ============================================================

LABEL_TO_INT = {
    "A": 0,
    "D": 1,
    "H": 2
}

INT_TO_LABEL = {
    0: "A",
    1: "D",
    2: "H"
}


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("V5 POISSON H/D/A EVALUATION")
print("=" * 70)

print("\nLoading V4 feature dataset...")

df = pd.read_csv(
    DATA_PATH
)

print(
    f"Dataset shape: {df.shape}"
)


# ============================================================
# LOAD RAW GOALS
# ============================================================

print("\nLoading raw match results...")

RAW_DIR = (
    BASE_DIR
    / "ml"
    / "data"
    / "raw"
)

raw_files = sorted(
    RAW_DIR.glob("*.csv")
)

raw_matches = []


for file in raw_files:

    try:

        raw = pd.read_csv(
            file,
            encoding="latin1"
        )

    except Exception:  # noqa: BLE001, S112

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


raw_df = pd.concat(
    raw_matches,
    ignore_index=True
)


# ============================================================
# CLEAN RAW DATA
# ============================================================

raw_df["Date"] = pd.to_datetime(
    raw_df["Date"],
    dayfirst=True,
    errors="coerce"
)

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)


raw_df["Date"] = (
    raw_df["Date"]
    .dt.normalize()
)

df["Date"] = (
    df["Date"]
    .dt.normalize()
)


for column in [
    "HomeTeam",
    "AwayTeam"
]:

    raw_df[column] = (
        raw_df[column]
        .astype(str)
        .str.strip()
    )

    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
    )


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


raw_df = raw_df.drop_duplicates(
    subset=[
        "Date",
        "HomeTeam",
        "AwayTeam"
    ],
    keep="first"
)


# ============================================================
# MERGE ACTUAL GOALS
# ============================================================

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


missing = df[
    df["FTHG"].isna()
    | df["FTAG"].isna()
]


if not missing.empty:

    raise ValueError(
        f"{len(missing)} matches are "
        "missing actual goals."
    )


# ============================================================
# TEST SET
# ============================================================

test_df = df[
    df["Season"] == TEST_SEASON
].copy()


if len(test_df) != 380:

    raise ValueError(
        f"Expected 380 test matches, "
        f"found {len(test_df)}."
    )


print(
    f"\nTest season: {TEST_SEASON}"
)

print(
    f"Test matches: {len(test_df)}"
)


# ============================================================
# LOAD MODELS
# ============================================================

print("\nLoading V5 goal models...")

home_bundle = joblib.load(
    HOME_MODEL_PATH
)

away_bundle = joblib.load(
    AWAY_MODEL_PATH
)


home_model = home_bundle["model"]
away_model = away_bundle["model"]

feature_columns = home_bundle["features"]


print(
    f"Number of model features: "
    f"{len(feature_columns)}"
)


# ============================================================
# PREPARE TEST FEATURES
# ============================================================

X_test = test_df[
    feature_columns
]


# ============================================================
# PREDICT EXPECTED GOALS
# ============================================================

print("\nGenerating expected goals...")

lambda_home = (
    home_model.predict(
        X_test
    )
)

lambda_away = (
    away_model.predict(
        X_test
    )
)


# ============================================================
# POISSON SCORE MATRIX
# ============================================================

def calculate_match_probabilities(
    home_lambda,
    away_lambda,
    max_goals=10
):

    home_goals = np.arange(
        0,
        max_goals + 1
    )

    away_goals = np.arange(
        0,
        max_goals + 1
    )


    home_probs = poisson.pmf(
        home_goals,
        home_lambda
    )

    away_probs = poisson.pmf(
        away_goals,
        away_lambda
    )


    score_matrix = (
        np.outer(
            home_probs,
            away_probs
        )
    )


    # --------------------------------------------------------
    # Normalize because we truncate at MAX_GOALS
    # --------------------------------------------------------

    total_probability = (
        score_matrix.sum()
    )


    if total_probability <= 0:

        raise ValueError(
            "Invalid Poisson probability "
            "matrix."
        )


    score_matrix /= (
        total_probability
    )


    # --------------------------------------------------------
    # Home win
    # --------------------------------------------------------

    home_probability = np.sum(
        np.tril(
            score_matrix,
            k=-1
        )
    )


    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

    draw_probability = np.trace(
        score_matrix
    )


    # --------------------------------------------------------
    # Away win
    # --------------------------------------------------------

    away_probability = np.sum(
        np.triu(
            score_matrix,
            k=1
        )
    )


    probabilities = np.array([
        away_probability,
        draw_probability,
        home_probability
    ])


    # Final normalization
    probabilities /= (
        probabilities.sum()
    )


    return probabilities, score_matrix


# ============================================================
# GENERATE MATCH PROBABILITIES
# ============================================================

print(
    "Building Poisson score distributions..."
)


probabilities = []

most_likely_scores = []


for h_lambda, a_lambda in zip(
    lambda_home,
    lambda_away
):

    probs, score_matrix = (
        calculate_match_probabilities(
            h_lambda,
            a_lambda,
            MAX_GOALS
        )
    )


    probabilities.append(
        probs
    )


    # Most likely score
    max_index = np.unravel_index(
        np.argmax(score_matrix),
        score_matrix.shape
    )


    most_likely_scores.append(
        f"{max_index[0]}-{max_index[1]}"
    )


probabilities = np.array(
    probabilities
)


# ============================================================
# VERIFY PROBABILITIES
# ============================================================

probability_sums = (
    probabilities.sum(axis=1)
)


print(
    "\nProbability validation:"
)

print(
    f"Minimum row sum: "
    f"{probability_sums.min():.10f}"
)

print(
    f"Maximum row sum: "
    f"{probability_sums.max():.10f}"
)


p_away = probabilities[:, 0]
p_draw = probabilities[:, 1]
p_home = probabilities[:, 2]


# ============================================================
# ACTUAL RESULTS
# ============================================================

actual_labels = (
    test_df["FTR"]
    .map(LABEL_TO_INT)
    .values
)


actual_label_strings = (
    test_df["FTR"]
    .values
)


# ============================================================
# PREDICTIONS
# ============================================================

predicted_indices = np.argmax(
    probabilities,
    axis=1
)


predicted_labels = np.array([
    INT_TO_LABEL[index]
    for index in predicted_indices
])


# ============================================================
# MAIN METRICS
# ============================================================

accuracy = accuracy_score(
    actual_labels,
    predicted_indices
)


logloss = log_loss(
    actual_labels,
    probabilities,
    labels=[0, 1, 2]
)


macro_f1 = f1_score(
    actual_labels,
    predicted_indices,
    average="macro",
    zero_division=0
)


print("\n" + "=" * 70)
print("V5 POISSON PERFORMANCE")
print("=" * 70)


print(
    f"\nAccuracy : {accuracy:.4f}"
)

print(
    f"Log Loss : {logloss:.4f}"
)

print(
    f"Macro F1 : {macro_f1:.4f}"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print(
    "\nClassification Report:"
)

print(
    classification_report(
        actual_labels,
        predicted_indices,
        labels=[0, 1, 2],
        target_names=[
            "Away",
            "Draw",
            "Home"
        ],
        zero_division=0
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    actual_labels,
    predicted_indices,
    labels=[0, 1, 2]
)


cm_df = pd.DataFrame(
    cm,
    index=[
        "Actual Away",
        "Actual Draw",
        "Actual Home"
    ],
    columns=[
        "Pred Away",
        "Pred Draw",
        "Pred Home"
    ]
)


print(
    "Confusion Matrix:"
)

print(
    cm_df.to_string()
)


# ============================================================
# AVERAGE PROBABILITIES
# ============================================================

print(
    "\nAverage predicted probabilities:"
)

print(
    f"  Away : {p_away.mean():.4f}"
)

print(
    f"  Draw : {p_draw.mean():.4f}"
)

print(
    f"  Home : {p_home.mean():.4f}"
)


# ============================================================
# PROBABILITIES BY ACTUAL RESULT
# ============================================================

probability_df = pd.DataFrame({

    "Actual":
        actual_label_strings,

    "P_Away":
        p_away,

    "P_Draw":
        p_draw,

    "P_Home":
        p_home

})


grouped = (
    probability_df
    .groupby("Actual")
    [["P_Away", "P_Draw", "P_Home"]]
    .mean()
    .reindex(
        ["A", "D", "H"]
    )
)


print(
    "\nMean probability by actual outcome:"
)

print(
    grouped.round(4)
)


# ============================================================
# DRAW ANALYSIS
# ============================================================

actual_draw_mask = (
    actual_labels == 1
)

non_draw_mask = (
    ~actual_draw_mask
)


draw_mean = (
    p_draw[
        actual_draw_mask
    ].mean()
)

non_draw_mean = (
    p_draw[
        non_draw_mask
    ].mean()
)


draw_median = np.median(
    p_draw[
        actual_draw_mask
    ]
)

non_draw_median = np.median(
    p_draw[
        non_draw_mask
    ]
)


print(
    "\n" + "=" * 70
)

print(
    "DRAW PROBABILITY ANALYSIS"
)

print(
    "=" * 70
)


print(
    f"\nActual Draw mean P(D): "
    f"{draw_mean:.4f}"
)

print(
    f"Non-Draw mean P(D): "
    f"{non_draw_mean:.4f}"
)

print(
    f"Difference: "
    f"{draw_mean - non_draw_mean:.4f}"
)

print(
    f"\nActual Draw median P(D): "
    f"{draw_median:.4f}"
)

print(
    f"Non-Draw median P(D): "
    f"{non_draw_median:.4f}"
)


# ============================================================
# DRAW RANK
# ============================================================

draw_ranks = []


for row in probabilities:

    ranking = np.argsort(
        row
    )[::-1]

    rank = (
        np.where(
            ranking == 1
        )[0][0]
        + 1
    )

    draw_ranks.append(
        rank
    )


draw_ranks = np.array(
    draw_ranks
)


actual_draw_ranks = (
    draw_ranks[
        actual_draw_mask
    ]
)


print(
    "\nDraw probability rank "
    "for actual draws:"
)


for rank in [1, 2, 3]:

    count = np.sum(
        actual_draw_ranks == rank
    )

    total = len(
        actual_draw_ranks
    )

    percentage = (
        count / total
    )

    print(
        f"  Rank {rank}: "
        f"{count}/{total} "
        f"({percentage:.2%})"
    )


# ============================================================
# PREDICTION DISTRIBUTION
# ============================================================

prediction_distribution = (
    pd.Series(
        predicted_labels
    )
    .value_counts()
    .reindex(
        ["A", "D", "H"]
    )
    .fillna(0)
    .astype(int)
)


print(
    "\nPrediction distribution:"
)

for label in ["A", "D", "H"]:

    count = (
        prediction_distribution[
            label
        ]
    )

    percentage = (
        count / len(test_df)
    )

    print(
        f"  {label}: "
        f"{count} "
        f"({percentage:.2%})"
    )


# ============================================================
# BRIER SCORES
# ============================================================

brier_away = brier_score_loss(
    (actual_labels == 0).astype(int),
    p_away
)

brier_draw = brier_score_loss(
    (actual_labels == 1).astype(int),
    p_draw
)

brier_home = brier_score_loss(
    (actual_labels == 2).astype(int),
    p_home
)


print(
    "\nBrier Scores:"
)

print(
    f"  Away : {brier_away:.4f}"
)

print(
    f"  Draw : {brier_draw:.4f}"
)

print(
    f"  Home : {brier_home:.4f}"
)


# ============================================================
# TOP DRAW PROBABILITY MATCHES
# ============================================================

results = test_df[
    [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTR"
    ]
].copy()


results["Pred_Home_Goals"] = (
    lambda_home
)

results["Pred_Away_Goals"] = (
    lambda_away
)

results["P_Away"] = (
    p_away
)

results["P_Draw"] = (
    p_draw
)

results["P_Home"] = (
    p_home
)

results["Predicted"] = (
    predicted_labels
)

results["Most_Likely_Score"] = (
    most_likely_scores
)

results["Draw_Rank"] = (
    draw_ranks
)


results = results.sort_values(
    "P_Draw",
    ascending=False
)


print(
    "\n" + "=" * 70
)

print(
    "TOP 15 MATCHES BY DRAW PROBABILITY"
)

print(
    "=" * 70
)


print(
    results
    .head(15)
    .round(4)
    .to_string(
        index=False
    )
)


# ============================================================
# SAVE MATCH PROBABILITIES
# ============================================================

results.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# SAVE V5 SUMMARY
# ============================================================

comparison = pd.DataFrame([{

    "model":
        "Poisson V5",

    "accuracy":
        accuracy,

    "log_loss":
        logloss,

    "macro_f1":
        macro_f1,

    "away_f1":
        f1_score(
            actual_labels,
            predicted_indices,
            labels=[0],
            average="macro",
            zero_division=0
        ),

    "draw_f1":
        f1_score(
            actual_labels,
            predicted_indices,
            labels=[1],
            average="macro",
            zero_division=0
        ),

    "home_f1":
        f1_score(
            actual_labels,
            predicted_indices,
            labels=[2],
            average="macro",
            zero_division=0
        ),

    "avg_p_away":
        p_away.mean(),

    "avg_p_draw":
        p_draw.mean(),

    "avg_p_home":
        p_home.mean(),

    "actual_draw_mean_p_draw":
        draw_mean,

    "non_draw_mean_p_draw":
        non_draw_mean,

    "draw_probability_gap":
        draw_mean - non_draw_mean,

    "draw_brier":
        brier_draw,

    "predicted_draws":
        int(
            prediction_distribution["D"]
        )

}])


comparison.to_csv(
    COMPARISON_PATH,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print(
    "\n" + "=" * 70
)

print(
    "V5 POISSON EVALUATION COMPLETE"
)

print(
    "=" * 70
)

print(
    f"""
Accuracy : {accuracy:.4f}
Log Loss : {logloss:.4f}
Macro F1 : {macro_f1:.4f}

Draw F1  : {comparison.iloc[0]["draw_f1"]:.4f}

Predicted Draws:
    {int(prediction_distribution["D"])} / 380

Actual Draw P(D):
    {draw_mean:.4f}

Non-Draw P(D):
    {non_draw_mean:.4f}

Draw Probability Gap:
    {draw_mean - non_draw_mean:.4f}
"""
)

print(
    "\nSaved:"
)

print(
    f"  {OUTPUT_PATH}"
)

print(
    f"  {COMPARISON_PATH}"
)

print("=" * 70)