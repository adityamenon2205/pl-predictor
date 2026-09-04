from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
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
    / "training_features_v3.csv"
)

MODEL_PATH = (
    BASE_DIR
    / "ml"
    / "models"
    / "random_forest_v3.pkl"
)

TEST_SEASON = "2025_26"

OUTPUT_DIR = (
    BASE_DIR
    / "ml"
    / "models"
)

RESULT_PATH = (
    OUTPUT_DIR
    / "probability_analysis.csv"
)

DRAW_MATCHES_PATH = (
    OUTPUT_DIR
    / "draw_match_probabilities.csv"
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
print("RF V3 PROBABILITY ANALYSIS")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")


# ============================================================
# LOAD MODEL
# ============================================================

print("\nLoading model...")

loaded_object = joblib.load(MODEL_PATH)


# ------------------------------------------------------------
# Support both:
#
# 1. Raw sklearn model
# 2. Dictionary model bundle
# ------------------------------------------------------------

if isinstance(loaded_object, dict):

    print("Model file format: dictionary bundle")

    model = loaded_object["model"]

    if "features" in loaded_object:
        feature_columns = loaded_object["features"]
    else:
        raise ValueError(
            "Model bundle does not contain 'features'."
        )

else:

    print("Model file format: raw sklearn model")

    model = loaded_object

    # --------------------------------------------------------
    # Raw model does not contain our saved feature list.
    # Reconstruct the feature list using the same exclusions
    # used during evaluation.
    # --------------------------------------------------------

    excluded_columns = {
        "Div",
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTR",
        "Season"
    }

    feature_columns = [
        column
        for column in df.columns
        if column not in excluded_columns
    ]


print(f"Model type: {type(model).__name__}")

print(
    f"Number of model features: "
    f"{len(feature_columns)}"
)


# ============================================================
# CHECK FEATURE COMPATIBILITY
# ============================================================

missing_features = [
    feature
    for feature in feature_columns
    if feature not in df.columns
]

if missing_features:

    raise ValueError(
        "The following model features are missing "
        f"from the dataset:\n{missing_features}"
    )


# ============================================================
# PREPARE TEST DATA
# ============================================================

test_df = df[
    df["Season"] == TEST_SEASON
].copy()

if test_df.empty:

    raise ValueError(
        f"No rows found for TEST_SEASON={TEST_SEASON}"
    )


print(
    f"\nTest season: {TEST_SEASON}"
)

print(
    f"Test matches: {len(test_df)}"
)


X_test = test_df[feature_columns]

actual_labels = (
    test_df["FTR"]
    .map(LABEL_TO_INT)
    .values
)


# ============================================================
# GET MODEL PROBABILITIES
# ============================================================

print("\nGenerating predictions...")

raw_probabilities = model.predict_proba(X_test)

model_classes = model.classes_

print(
    f"Model classes: {model_classes}"
)


# ============================================================
# NORMALIZE PROBABILITY ORDER
# ============================================================

def normalize_probabilities(
    probabilities,
    classes
):
    """
    Convert model probability columns into:

        column 0 = Away
        column 1 = Draw
        column 2 = Home
    """

    normalized = np.zeros(
        (len(probabilities), 3)
    )

    for i, class_value in enumerate(classes):

        if isinstance(
            class_value,
            str
        ):

            label = class_value

        else:

            label = INT_TO_LABEL.get(
                int(class_value)
            )

        if label not in LABEL_TO_INT:

            raise ValueError(
                f"Unknown model class: "
                f"{class_value}"
            )

        normalized[
            :,
            LABEL_TO_INT[label]
        ] = probabilities[:, i]

    return normalized


probabilities = normalize_probabilities(
    raw_probabilities,
    model_classes
)


# ============================================================
# EXTRACT INDIVIDUAL PROBABILITIES
# ============================================================

p_away = probabilities[:, 0]

p_draw = probabilities[:, 1]

p_home = probabilities[:, 2]


# ============================================================
# BASIC PREDICTIONS
# ============================================================

predicted_indices = np.argmax(
    probabilities,
    axis=1
)

predicted_labels = np.array([
    INT_TO_LABEL[i]
    for i in predicted_indices
])

actual_label_strings = np.array([
    INT_TO_LABEL[i]
    for i in actual_labels
])


# ============================================================
# BASIC METRICS
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


# ============================================================
# BRIER SCORES
# ============================================================

brier_scores = {}

for class_index, class_label in INT_TO_LABEL.items():

    binary_target = (
        actual_labels == class_index
    ).astype(int)

    brier_scores[class_label] = (
        brier_score_loss(
            binary_target,
            probabilities[:, class_index]
        )
    )


# ============================================================
# BASIC RESULTS
# ============================================================

print("\n" + "=" * 70)
print("BASIC MODEL PERFORMANCE")
print("=" * 70)

print(
    f"Accuracy : {accuracy:.4f}"
)

print(
    f"Log Loss : {logloss:.4f}"
)

print(
    f"Macro F1 : {macro_f1:.4f}"
)

print("\nBrier Scores:")

print(
    f"  Away : {brier_scores['A']:.4f}"
)

print(
    f"  Draw : {brier_scores['D']:.4f}"
)

print(
    f"  Home : {brier_scores['H']:.4f}"
)


# ============================================================
# AVERAGE PROBABILITY BY ACTUAL OUTCOME
# ============================================================

print("\n" + "=" * 70)
print(
    "AVERAGE PREDICTED PROBABILITY "
    "BY ACTUAL OUTCOME"
)
print("=" * 70)


probability_df = pd.DataFrame({

    "Actual": actual_label_strings,

    "P_Away": p_away,

    "P_Draw": p_draw,

    "P_Home": p_home,

    "Predicted": predicted_labels

})


grouped = (
    probability_df
    .groupby("Actual")
    [["P_Away", "P_Draw", "P_Home"]]
    .mean()
)

grouped = grouped.reindex(
    ["A", "D", "H"]
)


print("\n")
print(
    grouped.round(4)
)


# ============================================================
# MEDIAN PROBABILITY BY ACTUAL OUTCOME
# ============================================================

print("\n" + "=" * 70)
print(
    "MEDIAN PREDICTED PROBABILITY "
    "BY ACTUAL OUTCOME"
)
print("=" * 70)


median_grouped = (
    probability_df
    .groupby("Actual")
    [["P_Away", "P_Draw", "P_Home"]]
    .median()
)

median_grouped = median_grouped.reindex(
    ["A", "D", "H"]
)


print("\n")
print(
    median_grouped.round(4)
)


# ============================================================
# PROBABILITY RANK OF DRAW
# ============================================================

print("\n" + "=" * 70)
print("DRAW PROBABILITY RANK ANALYSIS")
print("=" * 70)


draw_rank = []

for i in range(
    len(probabilities)
):

    ordered = np.argsort(
        probabilities[i]
    )[::-1]

    draw_position = (
        np.where(
            ordered == 1
        )[0][0]
        + 1
    )

    draw_rank.append(
        draw_position
    )


draw_rank = np.array(
    draw_rank
)


rank_counts = (
    pd.Series(draw_rank)
    .value_counts()
    .sort_index()
)


print("\nAll matches:")

for rank in [1, 2, 3]:

    count = rank_counts.get(
        rank,
        0
    )

    print(
        f"Draw probability rank {rank}: "
        f"{count} matches"
    )


# ============================================================
# DRAW MATCHES ONLY
# ============================================================

actual_draw_mask = (
    actual_labels == 1
)

draw_match_ranks = (
    draw_rank[actual_draw_mask]
)


print("\nActual draw matches:")

total_draws = (
    len(draw_match_ranks)
)

for rank in [1, 2, 3]:

    count = np.sum(
        draw_match_ranks == rank
    )

    percentage = (
        count / total_draws
        if total_draws > 0
        else 0
    )

    print(
        f"Draw probability rank {rank}: "
        f"{count}/{total_draws} "
        f"({percentage:.2%})"
    )


# ============================================================
# DRAW PROBABILITY DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("DRAW PROBABILITY DISTRIBUTION")
print("=" * 70)


print(
    f"\nOverall mean P(D): "
    f"{p_draw.mean():.4f}"
)

print(
    f"Overall median P(D): "
    f"{np.median(p_draw):.4f}"
)


if actual_draw_mask.sum() > 0:

    print(
        f"Actual draw mean P(D): "
        f"{p_draw[actual_draw_mask].mean():.4f}"
    )

    print(
        f"Actual draw median P(D): "
        f"{np.median(p_draw[actual_draw_mask]):.4f}"
    )


# ============================================================
# NON-DRAW PROBABILITY
# ============================================================

non_draw_mask = (
    ~actual_draw_mask
)

print(
    f"\nNon-draw mean P(D): "
    f"{p_draw[non_draw_mask].mean():.4f}"
)

print(
    f"Non-draw median P(D): "
    f"{np.median(p_draw[non_draw_mask]):.4f}"
)


# ============================================================
# PREDICTION DISTRIBUTION
# ============================================================

print("\n" + "=" * 70)
print("MODEL PREDICTION DISTRIBUTION")
print("=" * 70)


prediction_counts = (
    pd.Series(predicted_labels)
    .value_counts()
    .reindex(
        ["A", "D", "H"]
    )
    .fillna(0)
    .astype(int)
)


print("\nPredicted:")

for label in ["A", "D", "H"]:

    count = prediction_counts[label]

    percentage = (
        count / len(test_df)
    )

    print(
        f"{label}: {count} "
        f"({percentage:.2%})"
    )


actual_counts = (
    pd.Series(actual_label_strings)
    .value_counts()
    .reindex(
        ["A", "D", "H"]
    )
    .fillna(0)
    .astype(int)
)


print("\nActual:")

for label in ["A", "D", "H"]:

    count = actual_counts[label]

    percentage = (
        count / len(test_df)
    )

    print(
        f"{label}: {count} "
        f"({percentage:.2%})"
    )


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("\n" + "=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)


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


print("\n")
print(cm_df)


# ============================================================
# ACTUAL DRAW MATCHES
# ============================================================

print("\n" + "=" * 70)
print("ACTUAL DRAW MATCH PROBABILITIES")
print("=" * 70)


draw_matches = test_df[
    actual_draw_mask
].copy()


draw_matches["P_Away"] = (
    p_away[actual_draw_mask]
)

draw_matches["P_Draw"] = (
    p_draw[actual_draw_mask]
)

draw_matches["P_Home"] = (
    p_home[actual_draw_mask]
)

draw_matches["Predicted"] = (
    predicted_labels[
        actual_draw_mask
    ]
)

draw_matches["Draw_Rank"] = (
    draw_match_ranks
)


display_columns = [
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
    "P_Away",
    "P_Draw",
    "P_Home",
    "Draw_Rank",
    "Predicted"
]


display_columns = [
    column
    for column in display_columns
    if column in draw_matches.columns
]


draw_matches_display = (
    draw_matches[
        display_columns
    ]
    .sort_values(
        "P_Draw",
        ascending=False
    )
)


print("\n")

if len(draw_matches_display) > 0:

    print(
        draw_matches_display
        .round(4)
        .to_string(index=False)
    )

else:

    print("No draw matches found.")


# ============================================================
# TOP 20 DRAW PROBABILITY MATCHES
# ============================================================

print("\n" + "=" * 70)
print(
    "TOP 20 MATCHES BY DRAW PROBABILITY"
)
print("=" * 70)


top_draw = probability_df.copy()


top_draw["Date"] = (
    test_df["Date"].values
)

top_draw["HomeTeam"] = (
    test_df["HomeTeam"].values
)

top_draw["AwayTeam"] = (
    test_df["AwayTeam"].values
)

top_draw["Actual"] = (
    actual_label_strings
)


top_draw = top_draw.sort_values(
    "P_Draw",
    ascending=False
)


top_draw_display = top_draw[
    [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "Actual",
        "P_Away",
        "P_Draw",
        "P_Home",
        "Predicted"
    ]
].head(20)


print("\n")

print(
    top_draw_display
    .round(4)
    .to_string(index=False)
)


# ============================================================
# HIGH DRAW PROBABILITY THRESHOLD ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print(
    "HIGH DRAW-PROBABILITY "
    "THRESHOLD ANALYSIS"
)
print("=" * 70)


threshold_results = []


for threshold in np.arange(
    0.15,
    0.36,
    0.01
):

    threshold = round(
        threshold,
        2
    )

    selected = (
        p_draw >= threshold
    )

    count = int(
        selected.sum()
    )


    if count == 0:
        continue


    actual_draws = int(
        actual_draw_mask.sum()
    )


    correct_draws = int(
        np.sum(
            selected
            & actual_draw_mask
        )
    )


    precision = (
        correct_draws / count
        if count > 0
        else 0
    )


    recall = (
        correct_draws / actual_draws
        if actual_draws > 0
        else 0
    )


    f1 = (
        2 * precision * recall
        / (precision + recall)
        if precision + recall > 0
        else 0
    )


    threshold_results.append({

        "threshold": threshold,

        "matches_selected": count,

        "actual_draws_captured":
            correct_draws,

        "draw_precision":
            precision,

        "draw_recall":
            recall,

        "draw_f1":
            f1

    })


threshold_df = pd.DataFrame(
    threshold_results
)


print("\n")

if not threshold_df.empty:

    print(
        threshold_df
        .round(4)
        .to_string(index=False)
    )

else:

    print(
        "No matches met the tested "
        "probability thresholds."
    )


# ============================================================
# SAVE DRAW MATCH DATA
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


draw_matches_display.to_csv(
    DRAW_MATCHES_PATH,
    index=False
)


# ============================================================
# SAVE SUMMARY
# ============================================================

summary_rows = []


for actual_label in [
    "A",
    "D",
    "H"
]:

    row = {

        "actual_outcome":
            actual_label,

        "mean_p_away":
            grouped.loc[
                actual_label,
                "P_Away"
            ],

        "mean_p_draw":
            grouped.loc[
                actual_label,
                "P_Draw"
            ],

        "mean_p_home":
            grouped.loc[
                actual_label,
                "P_Home"
            ],

        "median_p_away":
            median_grouped.loc[
                actual_label,
                "P_Away"
            ],

        "median_p_draw":
            median_grouped.loc[
                actual_label,
                "P_Draw"
            ],

        "median_p_home":
            median_grouped.loc[
                actual_label,
                "P_Home"
            ]

    }

    summary_rows.append(row)


summary_df = pd.DataFrame(
    summary_rows
)


summary_df.to_csv(
    RESULT_PATH,
    index=False
)


# ============================================================
# FINAL INTERPRETATION
# ============================================================

print("\n" + "=" * 70)
print("INTERPRETATION")
print("=" * 70)


print(
    f"""
The RF V3 model achieved:

Accuracy : {accuracy:.4f}
Log Loss : {logloss:.4f}
Macro F1 : {macro_f1:.4f}

Average probabilities:

Away : {p_away.mean():.4f}
Draw : {p_draw.mean():.4f}
Home : {p_home.mean():.4f}

Actual draw matches:
Mean P(D) = {
    p_draw[actual_draw_mask].mean()
    if actual_draw_mask.sum() > 0
    else 0
:.4f}

Non-draw matches:
Mean P(D) = {
    p_draw[non_draw_mask].mean()
:.4f}

This analysis is designed to determine whether
the model:

1. Recognizes draw-like matches,
2. Assigns reasonable draw probabilities but
   rarely ranks Draw first,
3. Systematically underestimates draws,
4. Or lacks enough predictive information to
   distinguish draws from wins.

The next modeling decision should be based on
these probability diagnostics rather than simply
forcing more Draw predictions.
"""
)


# ============================================================
# FILE OUTPUT
# ============================================================

print("\nFiles saved:")

print(
    f"  {RESULT_PATH}"
)

print(
    f"  {DRAW_MATCHES_PATH}"
)


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)