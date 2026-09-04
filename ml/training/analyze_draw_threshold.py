from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "training_features_v3.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "random_forest_v3.pkl"
)


# ============================================================
# CONFIGURATION
# ============================================================

TEST_SEASON = "2025_26"

LABEL_MAPPING = {
    "A": 0,
    "D": 1,
    "H": 2,
}

REVERSE_MAPPING = {
    0: "A",
    1: "D",
    2: "H",
}


# Draw thresholds we want to test
DRAW_THRESHOLDS = np.arange(
    0.20,
    0.41,
    0.01
)


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    print("Loading Random Forest V3...")

    saved_model = joblib.load(
        MODEL_FILE
    )

    if isinstance(saved_model, dict):

        model = saved_model["model"]

        features = saved_model.get(
            "features"
        )

    else:

        model = saved_model
        features = None

    print(
        "Model loaded successfully."
    )

    return model, features


# ============================================================
# LOAD TEST DATA
# ============================================================

def load_test_data(features):

    print(
        "\nLoading V3 feature dataset..."
    )

    df = pd.read_csv(
        DATA_FILE,
        parse_dates=["Date"]
    )

    print(
        f"Total matches: {len(df)}"
    )

    # --------------------------------------------------------
    # Select test season
    # --------------------------------------------------------

    test_df = df[
        df["Season"] == TEST_SEASON
    ].copy()

    print(
        f"Test season: {TEST_SEASON}"
    )

    print(
        f"Test matches: {len(test_df)}"
    )

    # --------------------------------------------------------
    # Feature columns
    # --------------------------------------------------------

    excluded_columns = [
        "Date",
        "Season",
        "HomeTeam",
        "AwayTeam",
        "FTR",
    ]

    if features is not None:

        X = test_df[
            features
        ]

    else:

        feature_columns = [
            column
            for column in test_df.columns
            if column not in excluded_columns
        ]

        X = test_df[
            feature_columns
        ]

    y = test_df["FTR"]

    print(
        f"Features used: {X.shape[1]}"
    )

    return X, y


# ============================================================
# GET MODEL PROBABILITIES
# ============================================================

def get_probabilities(model, X):

    probabilities_raw = model.predict_proba(
        X
    )

    model_classes = list(
        model.classes_
    )

    # --------------------------------------------------------
    # Reorder probabilities to:
    #
    # Away, Draw, Home
    # --------------------------------------------------------

    probability_columns = []

    for label in ["A", "D", "H"]:

        if label in model_classes:

            index = model_classes.index(
                label
            )

        else:

            index = model_classes.index(
                LABEL_MAPPING[label]
            )

        probability_columns.append(
            index
        )

    probabilities = probabilities_raw[
        :,
        probability_columns
    ]

    return probabilities


# ============================================================
# NORMAL ARGMAX PREDICTION
# ============================================================

def normal_predictions(probabilities):

    labels = [
        "A",
        "D",
        "H",
    ]

    predictions = []

    for row in probabilities:

        index = np.argmax(row)

        predictions.append(
            labels[index]
        )

    return predictions


# ============================================================
# DRAW THRESHOLD PREDICTION
# ============================================================

def threshold_predictions(
    probabilities,
    threshold,
):

    predictions = []

    for row in probabilities:

        away_probability = row[0]
        draw_probability = row[1]
        home_probability = row[2]

        # ----------------------------------------------------
        # If draw probability reaches threshold,
        # predict Draw.
        # ----------------------------------------------------

        if draw_probability >= threshold:

            prediction = "D"

        else:

            # Choose between Home and Away
            if home_probability >= away_probability:

                prediction = "H"

            else:

                prediction = "A"

        predictions.append(
            prediction
        )

    return predictions


# ============================================================
# EVALUATE PREDICTIONS
# ============================================================

def evaluate_predictions(
    y_true,
    predictions,
):

    accuracy = accuracy_score(
        y_true,
        predictions
    )

    draw_precision = precision_score(
        y_true,
        predictions,
        labels=["D"],
        average="macro",
        zero_division=0,
    )

    draw_recall = recall_score(
        y_true,
        predictions,
        labels=["D"],
        average="macro",
        zero_division=0,
    )

    draw_f1 = f1_score(
        y_true,
        predictions,
        labels=["D"],
        average="macro",
        zero_division=0,
    )

    macro_f1 = f1_score(
        y_true,
        predictions,
        labels=["H", "D", "A"],
        average="macro",
        zero_division=0,
    )

    draw_count = predictions.count("D")

    return {
        "Accuracy": accuracy,
        "Draw Precision": draw_precision,
        "Draw Recall": draw_recall,
        "Draw F1": draw_f1,
        "Macro F1": macro_f1,
        "Draw Predictions": draw_count,
    }


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model, features = load_model()

    # --------------------------------------------------------
    # Load test data
    # --------------------------------------------------------

    X_test, y_test = load_test_data(
        features
    )

    # --------------------------------------------------------
    # Get probabilities
    # --------------------------------------------------------

    probabilities = get_probabilities(
        model,
        X_test
    )

    # --------------------------------------------------------
    # Normal model
    # --------------------------------------------------------

    normal_preds = normal_predictions(
        probabilities
    )

    normal_results = evaluate_predictions(
        y_test,
        normal_preds
    )

    print("\n")
    print("=" * 90)
    print("BASELINE — NORMAL ARGMAX")
    print("=" * 90)

    print(
        f"Accuracy:         "
        f"{normal_results['Accuracy']:.4f}"
    )

    print(
        f"Draw Precision:   "
        f"{normal_results['Draw Precision']:.4f}"
    )

    print(
        f"Draw Recall:      "
        f"{normal_results['Draw Recall']:.4f}"
    )

    print(
        f"Draw F1:          "
        f"{normal_results['Draw F1']:.4f}"
    )

    print(
        f"Macro F1:         "
        f"{normal_results['Macro F1']:.4f}"
    )

    print(
        f"Draw Predictions: "
        f"{normal_results['Draw Predictions']}"
    )

    # --------------------------------------------------------
    # Test thresholds
    # --------------------------------------------------------

    results = []

    for threshold in DRAW_THRESHOLDS:

        predictions = threshold_predictions(
            probabilities,
            threshold
        )

        metrics = evaluate_predictions(
            y_test,
            predictions
        )

        results.append({
            "Draw Threshold": threshold,
            **metrics,
        })

    results_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print("\n")
    print("=" * 90)
    print("DRAW THRESHOLD ANALYSIS")
    print("=" * 90)

    print(
        results_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    # --------------------------------------------------------
    # Best by Accuracy
    # --------------------------------------------------------

    best_accuracy = results_df.loc[
        results_df["Accuracy"].idxmax()
    ]

    print("\n")
    print("=" * 90)
    print("BEST THRESHOLD BY ACCURACY")
    print("=" * 90)

    print(
        f"Threshold:        "
        f"{best_accuracy['Draw Threshold']:.2f}"
    )

    print(
        f"Accuracy:         "
        f"{best_accuracy['Accuracy']:.4f}"
    )

    print(
        f"Draw Precision:   "
        f"{best_accuracy['Draw Precision']:.4f}"
    )

    print(
        f"Draw Recall:      "
        f"{best_accuracy['Draw Recall']:.4f}"
    )

    print(
        f"Draw F1:          "
        f"{best_accuracy['Draw F1']:.4f}"
    )

    print(
        f"Macro F1:         "
        f"{best_accuracy['Macro F1']:.4f}"
    )

    print(
        f"Draw Predictions: "
        f"{int(best_accuracy['Draw Predictions'])}"
    )

    # --------------------------------------------------------
    # Best by Macro F1
    # --------------------------------------------------------

    best_macro = results_df.loc[
        results_df["Macro F1"].idxmax()
    ]

    print("\n")
    print("=" * 90)
    print("BEST THRESHOLD BY MACRO F1")
    print("=" * 90)

    print(
        f"Threshold:        "
        f"{best_macro['Draw Threshold']:.2f}"
    )

    print(
        f"Accuracy:         "
        f"{best_macro['Accuracy']:.4f}"
    )

    print(
        f"Draw Precision:   "
        f"{best_macro['Draw Precision']:.4f}"
    )

    print(
        f"Draw Recall:      "
        f"{best_macro['Draw Recall']:.4f}"
    )

    print(
        f"Draw F1:          "
        f"{best_macro['Draw F1']:.4f}"
    )

    print(
        f"Macro F1:         "
        f"{best_macro['Macro F1']:.4f}"
    )

    print(
        f"Draw Predictions: "
        f"{int(best_macro['Draw Predictions'])}"
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    output_file = (
        MODEL_FILE.parent
        / "draw_threshold_analysis.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nResults saved to:\n"
        f"{output_file}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()