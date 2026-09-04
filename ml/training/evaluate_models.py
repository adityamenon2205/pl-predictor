from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    log_loss,
)

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
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


# ============================================================
# MODELS TO EVALUATE
# ============================================================

MODELS = {
    "Random Forest V2": {
        "file": "random_forest_v2.pkl",
        "dataset": "training_features_v2.csv",
    },

    "Random Forest V3": {
        "file": "random_forest_v3.pkl",
        "dataset": "training_features_v3.csv",
    },

    "XGBoost V2": {
        "file": "xgboost_v2.pkl",
        "dataset": "training_features_v2.csv",
    },

    "XGBoost V2 Balanced": {
        "file": "xgboost_v2_balanced.pkl",
        "dataset": "training_features_v2.csv",
    },

    "XGBoost V3": {
        "file": "xgboost_v3.pkl",
        "dataset": "training_features_v3.csv",
    },
}


# ============================================================
# LOAD DATA
# ============================================================

def load_data(dataset_file):

    data_path = DATA_DIR / dataset_file

    print(f"Loading: {dataset_file}")

    df = pd.read_csv(
        data_path,
        parse_dates=["Date"]
    )

    print(f"Loaded {len(df)} matches.")

    return df


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data(df):

    excluded_columns = [
        "Date",
        "Season",
        "HomeTeam",
        "AwayTeam",
        "FTR",
    ]

    feature_columns = [
        column
        for column in df.columns
        if column not in excluded_columns
    ]

    X = df[feature_columns]

    y = df["FTR"]

    return X, y, feature_columns


# ============================================================
# EVALUATE ONE MODEL
# ============================================================

def evaluate_model(
    model_name,
    model_file,
    dataset_file,
):

    print("\n" + "=" * 70)
    print(f"Evaluating: {model_name}")
    print("=" * 70)

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model_path = MODEL_DIR / model_file

    if not model_path.exists():

        print(
            f"Model file not found: {model_path}"
        )

        return None

    saved_model = joblib.load(model_path)

    if isinstance(saved_model, dict):

        model = saved_model["model"]

        saved_features = saved_model.get(
            "features"
        )

    else:

        model = saved_model
        saved_features = None

    # --------------------------------------------------------
    # Load correct dataset
    # --------------------------------------------------------

    df = load_data(dataset_file)

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
    # Prepare features
    # --------------------------------------------------------

    excluded_columns = [
        "Date",
        "Season",
        "HomeTeam",
        "AwayTeam",
        "FTR",
    ]

    if saved_features is not None:

        missing_features = [
            feature
            for feature in saved_features
            if feature not in test_df.columns
        ]

        if missing_features:

            print(
                "\nMissing features:"
            )

            print(
                missing_features
            )

            return None

        X_test = test_df[
            saved_features
        ]

    else:

        feature_columns = [
            column
            for column in test_df.columns
            if column not in excluded_columns
        ]

        X_test = test_df[
            feature_columns
        ]

    y_test = test_df["FTR"]

    print(
        f"Features used: {X_test.shape[1]}"
    )

    # --------------------------------------------------------
    # Predictions
    # --------------------------------------------------------

    predictions_raw = model.predict(
    X_test
)

    # Handle both string labels ("H", "D", "A")
    # and encoded labels (0, 1, 2)
    predictions = []

    for prediction in predictions_raw:

        if isinstance(prediction, str):

            predictions.append(prediction)

        else:

            predictions.append(
                REVERSE_MAPPING[int(prediction)]
            )

    # --------------------------------------------------------
    # Probabilities
    # --------------------------------------------------------

    probabilities_raw = model.predict_proba(
    X_test
)

    # Reorder probability columns to:
    # Away, Draw, Home
    #
    # This works whether the model was trained
    # using encoded labels or string labels.

    model_classes = list(model.classes_)

    probability_columns = []

    for label in ["A", "D", "H"]:

        if label in model_classes:

            index = model_classes.index(label)

        else:

            index = model_classes.index(
                LABEL_MAPPING[label]
            )

        probability_columns.append(index)

    probabilities = probabilities_raw[
        :, probability_columns
    ]

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    loss = log_loss(
        y_test.map(LABEL_MAPPING),
        probabilities,
        labels=[0, 1, 2]
    )

    print(
        f"\nAccuracy: {accuracy:.4f}"
    )

    print(
        f"Log Loss: {loss:.4f}"
    )

    # --------------------------------------------------------
    # Classification report
    # --------------------------------------------------------

    report = classification_report(
        y_test,
        predictions,
        labels=["H", "D", "A"],
        target_names=[
            "Home Win",
            "Draw",
            "Away Win",
        ],
        output_dict=True,
        zero_division=0,
    )

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            labels=["H", "D", "A"],
            target_names=[
                "Home Win",
                "Draw",
                "Away Win",
            ],
            zero_division=0,
        )
    )

    # --------------------------------------------------------
    # Confusion matrix
    # --------------------------------------------------------

    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=["H", "D", "A"],
    )

    print("Confusion Matrix:")

    print(matrix)

    # --------------------------------------------------------
    # Probability analysis
    # --------------------------------------------------------

    probability_df = pd.DataFrame(
        probabilities,
        columns=[
            "Away",
            "Draw",
            "Home",
        ]
    )

    print(
        "\nAverage predicted probabilities:"
    )

    print(
        probability_df.mean()
    )

    # --------------------------------------------------------
    # Return metrics
    # --------------------------------------------------------

    return {
        "Model": model_name,
        "Accuracy": accuracy,
        "Log Loss": loss,
        "Home F1": report["Home Win"]["f1-score"],
        "Draw F1": report["Draw"]["f1-score"],
        "Away F1": report["Away Win"]["f1-score"],
        "Macro F1": report["macro avg"]["f1-score"],
        "Home Recall": report["Home Win"]["recall"],
        "Draw Recall": report["Draw"]["recall"],
        "Away Recall": report["Away Win"]["recall"],
    }

# ============================================================
# MAIN
# ============================================================

def main():

    results = []

    # --------------------------------------------------------
    # Evaluate each model using its correct feature dataset
    # --------------------------------------------------------

    for model_name, model_info in MODELS.items():

        result = evaluate_model(
            model_name,
            model_info["file"],
            model_info["dataset"],
        )

        if result is not None:

            results.append(result)

    # --------------------------------------------------------
    # Comparison table
    # --------------------------------------------------------

    if not results:

        print(
            "\nNo models were successfully evaluated."
        )

        return

    results_df = pd.DataFrame(
        results
    )

    results_df = results_df.sort_values(
        "Accuracy",
        ascending=False
    )

    print("\n")
    print("=" * 100)
    print("MODEL COMPARISON")
    print("=" * 100)

    print(
        results_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    # --------------------------------------------------------
    # Save results
    # --------------------------------------------------------

    output_file = (
        MODEL_DIR
        / "model_comparison.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nComparison saved to:\n"
        f"{output_file}"
    )
# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()