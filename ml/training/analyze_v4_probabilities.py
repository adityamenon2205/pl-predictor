from pathlib import Path

import joblib
import numpy as np
import pandas as pd
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

TEST_SEASON = "2025_26"

OUTPUT_PATH = (
    MODEL_DIR
    / "v4_probability_comparison.csv"
)

DRAW_DETAILS_PATH = (
    MODEL_DIR
    / "v4_draw_probability_details.csv"
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
# MODEL FILES
# ============================================================

MODEL_FILES = {
    "Random Forest V4":
        MODEL_DIR / "random_forest_v4.pkl",

    "XGBoost V4 Balanced":
        MODEL_DIR / "xgboost_v4_balanced.pkl"
}


# ============================================================
# PROBABILITY NORMALIZATION
# ============================================================

def normalize_probabilities(
    probabilities,
    classes
):
    """
    Convert model probability output into:

        column 0 = Away
        column 1 = Draw
        column 2 = Home

    Then normalize each row so that:

        P(A) + P(D) + P(H) = 1
    """

    normalized = np.zeros(
        (len(probabilities), 3),
        dtype=float
    )

    for i, class_value in enumerate(classes):

        # ----------------------------------------------------
        # String labels
        # ----------------------------------------------------

        if isinstance(
            class_value,
            str
        ):

            label = class_value

        # ----------------------------------------------------
        # Integer labels
        # ----------------------------------------------------

        else:

            class_int = int(
                class_value
            )

            if class_int not in INT_TO_LABEL:

                raise ValueError(
                    f"Unknown numeric class: "
                    f"{class_value}"
                )

            label = INT_TO_LABEL[
                class_int
            ]

        # ----------------------------------------------------
        # Validate label
        # ----------------------------------------------------

        if label not in LABEL_TO_INT:

            raise ValueError(
                f"Unknown class label: "
                f"{label}"
            )

        target_column = (
            LABEL_TO_INT[label]
        )

        normalized[
            :,
            target_column
        ] = probabilities[:, i]


    # --------------------------------------------------------
    # Normalize rows
    # --------------------------------------------------------

    row_sums = (
        normalized.sum(axis=1)
    )

    if np.any(
        row_sums <= 0
    ):

        raise ValueError(
            "At least one prediction has "
            "a probability sum <= 0."
        )

    normalized = (
        normalized
        / row_sums[:, np.newaxis]
    )

    return normalized


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("V4 PROBABILITY DIAGNOSTICS")
print("=" * 70)

print("\nLoading V4 dataset...")

df = pd.read_csv(
    DATA_PATH
)

print(
    f"Dataset shape: {df.shape}"
)


# ============================================================
# PREPARE TEST SET
# ============================================================

test_df = df[
    df["Season"] == TEST_SEASON
].copy()

if test_df.empty:

    raise ValueError(
        f"No data found for "
        f"{TEST_SEASON}"
    )


print(
    f"\nTest season: {TEST_SEASON}"
)

print(
    f"Test matches: {len(test_df)}"
)


# ============================================================
# RESULTS STORAGE
# ============================================================

comparison_results = []

all_draw_details = []


# ============================================================
# ANALYZE EACH MODEL
# ============================================================

for model_name, model_path in MODEL_FILES.items():

    print("\n" + "=" * 70)

    print(
        f"ANALYZING: {model_name}"
    )

    print("=" * 70)


    # ========================================================
    # LOAD MODEL
    # ========================================================

    print(
        f"\nLoading: {model_path.name}"
    )

    loaded_object = joblib.load(
        model_path
    )


    # --------------------------------------------------------
    # Support saved model bundles
    # --------------------------------------------------------

    if isinstance(
        loaded_object,
        dict
    ):

        if "model" not in loaded_object:

            raise ValueError(
                f"{model_name} bundle does "
                "not contain 'model'."
            )

        model = loaded_object[
            "model"
        ]

        if "features" not in loaded_object:

            raise ValueError(
                f"{model_name} bundle does "
                "not contain 'features'."
            )

        feature_columns = (
            loaded_object[
                "features"
            ]
        )

    # --------------------------------------------------------
    # Support raw sklearn models
    # --------------------------------------------------------

    else:

        model = loaded_object

        excluded_columns = {
            "Date",
            "Season",
            "HomeTeam",
            "AwayTeam",
            "FTR"
        }

        feature_columns = [
            column
            for column in df.columns
            if column not in excluded_columns
        ]


    print(
        f"Model type: "
        f"{type(model).__name__}"
    )

    print(
        f"Model features: "
        f"{len(feature_columns)}"
    )


    # ========================================================
    # TEST FEATURES
    # ========================================================

    X_test = test_df[
        feature_columns
    ]


    actual_labels = (
        test_df["FTR"]
        .map(LABEL_TO_INT)
        .values
    )


    # ========================================================
    # PREDICT
    # ========================================================

    raw_probabilities = (
        model.predict_proba(
            X_test
        )
    )


    normalized_probabilities = (
        normalize_probabilities(
            raw_probabilities,
            model.classes_
        )
    )


    # --------------------------------------------------------
    # Verify probabilities
    # --------------------------------------------------------

    probability_sums = (
        normalized_probabilities.sum(
            axis=1
        )
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


    # ========================================================
    # INDIVIDUAL PROBABILITIES
    # ========================================================

    p_away = (
        normalized_probabilities[:, 0]
    )

    p_draw = (
        normalized_probabilities[:, 1]
    )

    p_home = (
        normalized_probabilities[:, 2]
    )


    # ========================================================
    # PREDICTIONS
    # ========================================================

    predicted_indices = (
        np.argmax(
            normalized_probabilities,
            axis=1
        )
    )


    predicted_labels = np.array([
        INT_TO_LABEL[index]
        for index in predicted_indices
    ])


    actual_label_strings = np.array([
        INT_TO_LABEL[index]
        for index in actual_labels
    ])


    # ========================================================
    # METRICS
    # ========================================================

    accuracy = accuracy_score(
        actual_labels,
        predicted_indices
    )


    logloss = log_loss(
        actual_labels,
        normalized_probabilities,
        labels=[0, 1, 2]
    )


    macro_f1 = f1_score(
        actual_labels,
        predicted_indices,
        average="macro",
        zero_division=0
    )


    report = classification_report(
        actual_labels,
        predicted_indices,
        labels=[0, 1, 2],
        target_names=[
            "Away",
            "Draw",
            "Home"
        ],
        output_dict=True,
        zero_division=0
    )


    # ========================================================
    # BRIER SCORES
    # ========================================================

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


    # ========================================================
    # PRINT BASIC RESULTS
    # ========================================================

    print("\nPerformance:")

    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"Log Loss : {logloss:.4f}"
    )

    print(
        f"Macro F1 : {macro_f1:.4f}"
    )


    print("\nClassification Report:")

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


    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

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


    # ========================================================
    # AVERAGE PROBABILITIES
    # ========================================================

    print(
        "\nAverage predicted probabilities:"
    )

    print(
        f"  Away : "
        f"{p_away.mean():.4f}"
    )

    print(
        f"  Draw : "
        f"{p_draw.mean():.4f}"
    )

    print(
        f"  Home : "
        f"{p_home.mean():.4f}"
    )


    # ========================================================
    # ACTUAL OUTCOME PROBABILITIES
    # ========================================================

    probability_df = pd.DataFrame({

        "Actual":
            actual_label_strings,

        "P_Away":
            p_away,

        "P_Draw":
            p_draw,

        "P_Home":
            p_home,

        "Predicted":
            predicted_labels

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


    median_grouped = (
        probability_df
        .groupby("Actual")
        [["P_Away", "P_Draw", "P_Home"]]
        .median()
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


    print(
        "\nMedian probability by actual outcome:"
    )

    print(
        median_grouped.round(4)
    )


    # ========================================================
    # DRAW ANALYSIS
    # ========================================================

    actual_draw_mask = (
        actual_labels == 1
    )

    non_draw_mask = (
        ~actual_draw_mask
    )


    # --------------------------------------------------------
    # Draw probability
    # --------------------------------------------------------

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


    draw_median = (
        np.median(
            p_draw[
                actual_draw_mask
            ]
        )
    )

    non_draw_median = (
        np.median(
            p_draw[
                non_draw_mask
            ]
        )
    )


    print(
        "\nDraw probability:"
    )

    print(
        f"Actual Draw mean P(D): "
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
        f"Actual Draw median P(D): "
        f"{draw_median:.4f}"
    )

    print(
        f"Non-Draw median P(D): "
        f"{non_draw_median:.4f}"
    )


    # ========================================================
    # DRAW PROBABILITY RANK
    # ========================================================

    draw_ranks = []


    for row in normalized_probabilities:

        ordered = np.argsort(
            row
        )[::-1]

        rank = (
            np.where(
                ordered == 1
            )[0][0]
            + 1
        )

        draw_ranks.append(
            rank
        )


    draw_ranks = np.array(
        draw_ranks
    )


    print(
        "\nDraw probability rank "
        "for actual draws:"
    )


    draw_match_ranks = (
        draw_ranks[
            actual_draw_mask
        ]
    )


    for rank in [1, 2, 3]:

        count = np.sum(
            draw_match_ranks == rank
        )

        total = len(
            draw_match_ranks
        )

        percentage = (
            count / total
            if total > 0
            else 0
        )

        print(
            f"  Rank {rank}: "
            f"{count}/{total} "
            f"({percentage:.2%})"
        )


    # ========================================================
    # DRAW PREDICTION COUNT
    # ========================================================

    prediction_counts = (
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
            prediction_counts[label]
        )

        percentage = (
            count / len(test_df)
        )

        print(
            f"  {label}: "
            f"{count} "
            f"({percentage:.2%})"
        )


    # ========================================================
    # TOP DRAW PROBABILITY MATCHES
    # ========================================================

    top_draw = pd.DataFrame({

        "Date":
            test_df["Date"].values,

        "HomeTeam":
            test_df["HomeTeam"].values,

        "AwayTeam":
            test_df["AwayTeam"].values,

        "Actual":
            actual_label_strings,

        "P_Away":
            p_away,

        "P_Draw":
            p_draw,

        "P_Home":
            p_home,

        "Predicted":
            predicted_labels,

        "Draw_Rank":
            draw_ranks

    })


    top_draw = (
        top_draw
        .sort_values(
            "P_Draw",
            ascending=False
        )
    )


    print(
        "\nTop 15 matches by P(D):"
    )

    print(
        top_draw
        .head(15)
        .round(4)
        .to_string(
            index=False
        )
    )


    # ========================================================
    # ACTUAL DRAW MATCH DETAILS
    # ========================================================

    draw_details = (
        top_draw[
            top_draw["Actual"] == "D"
        ]
        .copy()
    )


    draw_details.insert(
        0,
        "Model",
        model_name
    )


    all_draw_details.append(
        draw_details
    )


    # ========================================================
    # STORE COMPARISON RESULT
    # ========================================================

    comparison_results.append({

        "model":
            model_name,

        "accuracy":
            accuracy,

        "log_loss":
            logloss,

        "macro_f1":
            macro_f1,

        "draw_precision":
            report["Draw"]["precision"],

        "draw_recall":
            report["Draw"]["recall"],

        "draw_f1":
            report["Draw"]["f1-score"],

        "home_f1":
            report["Home"]["f1-score"],

        "away_f1":
            report["Away"]["f1-score"],

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

        "actual_draw_median_p_draw":
            draw_median,

        "non_draw_median_p_draw":
            non_draw_median,

        "draw_rank_1_count":
            np.sum(
                draw_match_ranks == 1
            ),

        "draw_rank_2_count":
            np.sum(
                draw_match_ranks == 2
            ),

        "draw_rank_3_count":
            np.sum(
                draw_match_ranks == 3
            ),

        "draw_brier":
            brier_draw,

        "away_brier":
            brier_away,

        "home_brier":
            brier_home,

        "predicted_draws":
            int(
                prediction_counts["D"]
            )

    })


# ============================================================
# COMPARISON TABLE
# ============================================================

comparison_df = pd.DataFrame(
    comparison_results
)


comparison_df = (
    comparison_df
    .sort_values(
        "log_loss"
    )
)


print("\n" + "=" * 70)
print("V4 PROBABILITY COMPARISON")
print("=" * 70)


print(
    comparison_df
    .round(4)
    .to_string(index=False)
)


# ============================================================
# SAVE COMPARISON
# ============================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


comparison_df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ============================================================
# SAVE DRAW DETAILS
# ============================================================

if all_draw_details:

    combined_draw_details = pd.concat(
        all_draw_details,
        ignore_index=True
    )

    combined_draw_details.to_csv(
        DRAW_DETAILS_PATH,
        index=False
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("V4 PROBABILITY ANALYSIS COMPLETE")
print("=" * 70)


best_accuracy = (
    comparison_df
    .loc[
        comparison_df["accuracy"].idxmax()
    ]
)


best_macro_f1 = (
    comparison_df
    .loc[
        comparison_df["macro_f1"].idxmax()
    ]
)


best_draw_f1 = (
    comparison_df
    .loc[
        comparison_df["draw_f1"].idxmax()
    ]
)


best_draw_gap = (
    comparison_df
    .loc[
        comparison_df["draw_probability_gap"].idxmax()
    ]
)


print(
    f"""
Best Accuracy:
    {best_accuracy['model']}
    {best_accuracy['accuracy']:.4f}

Best Macro F1:
    {best_macro_f1['model']}
    {best_macro_f1['macro_f1']:.4f}

Best Draw F1:
    {best_draw_f1['model']}
    {best_draw_f1['draw_f1']:.4f}

Largest Draw Probability Gap:
    {best_draw_gap['model']}
    {best_draw_gap['draw_probability_gap']:.4f}
"""
)


print(
    "\nOutput files:"
)

print(
    f"  {OUTPUT_PATH}"
)

print(
    f"  {DRAW_DETAILS_PATH}"
)


print("=" * 70)