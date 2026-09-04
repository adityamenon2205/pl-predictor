from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    log_loss,
)
from sklearn.model_selection import TimeSeriesSplit


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

# Number of temporal folds used to generate
# out-of-fold calibration probabilities.
N_SPLITS = 5

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

    print("Model loaded successfully.")

    return model, features


# ============================================================
# LOAD DATA
# ============================================================

def load_data(features):

    print(
        "\nLoading V3 feature dataset..."
    )

    df = pd.read_csv(
        DATA_FILE,
        parse_dates=["Date"]
    )

    # --------------------------------------------------------
    # Make sure data is in chronological order
    # --------------------------------------------------------

    df = df.sort_values(
        "Date"
    ).reset_index(
        drop=True
    )

    print(
        f"Total matches: {len(df)}"
    )

    # --------------------------------------------------------
    # Select model features
    # --------------------------------------------------------

    excluded_columns = [
        "Date",
        "Season",
        "HomeTeam",
        "AwayTeam",
        "FTR",
    ]

    if features is None:

        features = [
            column
            for column in df.columns
            if column not in excluded_columns
        ]

    X = df[
        features
    ].copy()

    y = df[
        "FTR"
    ].copy()

    return df, X, y, features


# ============================================================
# ENCODE LABELS
# ============================================================

def encode_labels(y):

    encoded = y.map(
        LABEL_MAPPING
    )

    if encoded.isna().any():

        invalid_labels = y[
            encoded.isna()
        ].unique()

        raise ValueError(
            f"Unknown target labels found: "
            f"{invalid_labels}"
        )

    return encoded.astype(int)


# ============================================================
# REORDER PROBABILITIES
# ============================================================

def reorder_probabilities(
    probabilities,
    classes,
):

    classes = list(classes)

    column_indices = []

    for label in [
        "A",
        "D",
        "H",
    ]:

        if label in classes:

            index = classes.index(
                label
            )

        elif LABEL_MAPPING[label] in classes:

            index = classes.index(
                LABEL_MAPPING[label]
            )

        else:

            raise ValueError(
                f"Could not find class "
                f"{label} in model classes: "
                f"{classes}"
            )

        column_indices.append(
            index
        )

    return probabilities[
        :,
        column_indices
    ]


# ============================================================
# GET MODEL PROBABILITIES
# ============================================================

def get_probabilities(
    model,
    X,
):

    probabilities_raw = (
        model.predict_proba(X)
    )

    return reorder_probabilities(
        probabilities_raw,
        model.classes_,
    )


# ============================================================
# TEMPORAL OUT-OF-FOLD PROBABILITIES
# ============================================================

def generate_oof_probabilities(
    base_model,
    X,
    y,
):

    print("\n")
    print("=" * 90)
    print("GENERATING TEMPORAL OUT-OF-FOLD PROBABILITIES")
    print("=" * 90)

    print(
        f"Temporal folds: {N_SPLITS}"
    )

    # --------------------------------------------------------
    # Convert target to numeric labels
    # --------------------------------------------------------

    y_encoded = encode_labels(
        y
    ).values

    # --------------------------------------------------------
    # Storage for OOF predictions
    #
    # Rows that are not yet predicted remain NaN.
    # --------------------------------------------------------

    oof_probabilities = np.full(
        (
            len(X),
            3,
        ),
        np.nan,
    )

    # --------------------------------------------------------
    # TimeSeriesSplit
    #
    # Every validation block is predicted by a model trained
    # ONLY on earlier matches.
    # --------------------------------------------------------

    tscv = TimeSeriesSplit(
        n_splits=N_SPLITS
    )

    for fold, (
        train_indices,
        validation_indices,
    ) in enumerate(
        tscv.split(X),
        start=1,
    ):

        print(
            f"\nFold {fold}/{N_SPLITS}"
        )

        print(
            f"Training matches: "
            f"{len(train_indices)}"
        )

        print(
            f"Validation matches: "
            f"{len(validation_indices)}"
        )

        # ----------------------------------------------------
        # Clone the original RF.
        #
        # This creates a fresh model with the same parameters.
        # ----------------------------------------------------

        fold_model = clone(
            base_model
        )

        # ----------------------------------------------------
        # Train ONLY on earlier matches
        # ----------------------------------------------------

        fold_model.fit(
            X.iloc[train_indices],
            y.iloc[train_indices],
        )

        # ----------------------------------------------------
        # Predict probabilities on future validation block
        # ----------------------------------------------------

        fold_probabilities = (
            get_probabilities(
                fold_model,
                X.iloc[
                    validation_indices
                ],
            )
        )

        oof_probabilities[
            validation_indices
        ] = fold_probabilities

    # --------------------------------------------------------
    # Keep only rows that received OOF predictions.
    # --------------------------------------------------------

    valid_mask = ~np.isnan(
        oof_probabilities
    ).any(
        axis=1
    )

    valid_probabilities = (
        oof_probabilities[
            valid_mask
        ]
    )

    valid_targets = (
        y_encoded[
            valid_mask
        ]
    )

    print(
        f"\nOOF predictions generated: "
        f"{len(valid_probabilities)}"
    )

    print(
        f"Rows excluded from calibration: "
        f"{len(X) - len(valid_probabilities)}"
    )

    return (
        valid_probabilities,
        valid_targets,
    )


# ============================================================
# TRAIN CALIBRATION MODELS
# ============================================================

def train_calibrators(
    probabilities,
    targets,
    method,
):

    print(
        f"\nTraining {method} calibration..."
    )

    calibrators = []

    # --------------------------------------------------------
    # Train one-vs-rest calibrator for each outcome:
    #
    # 0 = Away
    # 1 = Draw
    # 2 = Home
    # --------------------------------------------------------

    for class_index in range(3):

        class_probability = (
            probabilities[
                :,
                class_index
            ]
        )

        class_target = (
            targets == class_index
        ).astype(int)

        # ----------------------------------------------------
        # Sigmoid / Platt-style calibration
        # ----------------------------------------------------

        if method == "sigmoid":

            calibrator = LogisticRegression(
                max_iter=1000
            )

            calibrator.fit(
                class_probability.reshape(
                    -1,
                    1
                ),
                class_target,
            )

        # ----------------------------------------------------
        # Isotonic calibration
        # ----------------------------------------------------

        elif method == "isotonic":

            calibrator = IsotonicRegression(
                y_min=0,
                y_max=1,
                out_of_bounds="clip",
            )

            calibrator.fit(
                class_probability,
                class_target,
            )

        else:

            raise ValueError(
                f"Unknown calibration method: "
                f"{method}"
            )

        calibrators.append(
            calibrator
        )

    return calibrators


# ============================================================
# CALIBRATED MODEL WRAPPER
# ============================================================

class ProbabilityCalibrator:

    def __init__(
        self,
        base_model,
        calibrators,
        method,
    ):

        self.base_model = base_model
        self.calibrators = calibrators
        self.method = method

        # Internal class representation:
        # 0 = Away
        # 1 = Draw
        # 2 = Home
        self.classes_ = np.array(
            [0, 1, 2]
        )

    def predict_proba(
        self,
        X,
    ):

        # ----------------------------------------------------
        # Get raw RF probabilities
        # ----------------------------------------------------

        raw_probabilities = (
            get_probabilities(
                self.base_model,
                X,
            )
        )

        calibrated_probabilities = []

        # ----------------------------------------------------
        # Apply each calibration model
        # ----------------------------------------------------

        for class_index, calibrator in enumerate(
            self.calibrators
        ):

            class_probability = (
                raw_probabilities[
                    :,
                    class_index
                ]
            )

            if self.method == "sigmoid":

                calibrated_probability = (
                    calibrator.predict_proba(
                        class_probability.reshape(
                            -1,
                            1
                        )
                    )[:, 1]
                )

            else:

                calibrated_probability = (
                    calibrator.predict(
                        class_probability
                    )
                )

            calibrated_probabilities.append(
                calibrated_probability
            )

        # ----------------------------------------------------
        # Convert list to matrix
        # ----------------------------------------------------

        calibrated_probabilities = (
            np.column_stack(
                calibrated_probabilities
            )
        )

        # ----------------------------------------------------
        # Normalize probabilities
        #
        # Because each one-vs-rest calibrator works separately,
        # their outputs may not sum exactly to 1.
        # ----------------------------------------------------

        probability_sum = (
            calibrated_probabilities.sum(
                axis=1,
                keepdims=True,
            )
        )

        probability_sum[
            probability_sum == 0
        ] = 1

        calibrated_probabilities = (
            calibrated_probabilities
            / probability_sum
        )

        return calibrated_probabilities


# ============================================================
# EVALUATE MODEL
# ============================================================

def evaluate_model(
    model_name,
    model,
    X,
    y,
):

    probabilities = get_probabilities(
        model,
        X,
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    class_labels = [
        "A",
        "D",
        "H",
    ]

    predictions = [
        class_labels[
            np.argmax(row)
        ]
        for row in probabilities
    ]

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y,
        predictions,
    )

    encoded_y = encode_labels(
        y
    )

    loss = log_loss(
        encoded_y,
        probabilities,
        labels=[
            0,
            1,
            2,
        ],
    )

    macro_f1 = f1_score(
        y,
        predictions,
        labels=[
            "H",
            "D",
            "A",
        ],
        average="macro",
        zero_division=0,
    )

    print("\n")
    print("=" * 90)
    print(model_name)
    print("=" * 90)

    print(
        f"Accuracy:  {accuracy:.4f}"
    )

    print(
        f"Log Loss:  {loss:.4f}"
    )

    print(
        f"Macro F1:  {macro_f1:.4f}"
    )

    print(
        "\nAverage predicted probabilities:"
    )

    print(
        f"Away: {probabilities[:, 0].mean():.4f}"
    )

    print(
        f"Draw: {probabilities[:, 1].mean():.4f}"
    )

    print(
        f"Home: {probabilities[:, 2].mean():.4f}"
    )

    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y,
            predictions,
            labels=[
                "H",
                "D",
                "A",
            ],
            target_names=[
                "Home Win",
                "Draw",
                "Away Win",
            ],
            zero_division=0,
        )
    )

    return {
        "Accuracy": accuracy,
        "Log Loss": loss,
        "Macro F1": macro_f1,
        "Draw Recall": recall_draw(
            y,
            predictions,
        ),
        "Draw F1": draw_f1(
            y,
            predictions,
        ),
    }


# ============================================================
# DRAW METRICS
# ============================================================

def recall_draw(
    y_true,
    predictions,
):

    from sklearn.metrics import recall_score

    return recall_score(
        y_true,
        predictions,
        labels=["D"],
        average="macro",
        zero_division=0,
    )


def draw_f1(
    y_true,
    predictions,
):

    from sklearn.metrics import f1_score

    return f1_score(
        y_true,
        predictions,
        labels=["D"],
        average="macro",
        zero_division=0,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # Load original trained RF V3
    # --------------------------------------------------------

    base_model, features = load_model()

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    df, X, y, features = load_data(
        features
    )

    print(
        f"Features used: {len(features)}"
    )

    # ========================================================
    # FINAL TEST SET
    # ========================================================

    test_mask = (
        df["Season"] == TEST_SEASON
    )

    X_test = X.loc[
        test_mask
    ].copy()

    y_test = y.loc[
        test_mask
    ].copy()

    # ========================================================
    # CALIBRATION DATA
    # ========================================================

    calibration_mask = (
        df["Season"] != TEST_SEASON
    )

    X_calibration = X.loc[
        calibration_mask
    ].copy()

    y_calibration = y.loc[
        calibration_mask
    ].copy()

    print("\n")
    print("=" * 90)
    print("DATA SPLIT")
    print("=" * 90)

    print(
        f"Calibration matches: "
        f"{len(X_calibration)}"
    )

    print(
        f"Final test matches: "
        f"{len(X_test)}"
    )

    print(
        f"Final test season: "
        f"{TEST_SEASON}"
    )

    # ========================================================
    # GENERATE OOF PROBABILITIES
    # ========================================================

    oof_probabilities, oof_targets = (
        generate_oof_probabilities(
            base_model,
            X_calibration,
            y_calibration,
        )
    )

    # ========================================================
    # BASELINE
    # ========================================================

    baseline_results = evaluate_model(
        "BASELINE — RF V3",
        base_model,
        X_test,
        y_test,
    )

    # ========================================================
    # CALIBRATION METHODS
    # ========================================================

    methods = [
        "sigmoid",
        "isotonic",
    ]

    results = []

    for method in methods:

        print("\n")
        print("=" * 90)
        print(
            f"CALIBRATION METHOD: "
            f"{method.upper()}"
        )
        print("=" * 90)

        # ----------------------------------------------------
        # Train calibrators using ONLY temporal OOF predictions
        # ----------------------------------------------------

        calibrators = train_calibrators(
            oof_probabilities,
            oof_targets,
            method,
        )

        # ----------------------------------------------------
        # Wrap the untouched RF V3
        # ----------------------------------------------------

        calibrated_model = (
            ProbabilityCalibrator(
                base_model,
                calibrators,
                method,
            )
        )

        # ----------------------------------------------------
        # Evaluate on untouched 2025/26
        # ----------------------------------------------------

        calibrated_results = evaluate_model(
            f"CALIBRATED — {method.upper()}",
            calibrated_model,
            X_test,
            y_test,
        )

        results.append({
            "Model": (
                f"RF V3 + "
                f"{method.capitalize()}"
            ),
            "Accuracy": (
                calibrated_results[
                    "Accuracy"
                ]
            ),
            "Log Loss": (
                calibrated_results[
                    "Log Loss"
                ]
            ),
            "Macro F1": (
                calibrated_results[
                    "Macro F1"
                ]
            ),
            "Draw Recall": (
                calibrated_results[
                    "Draw Recall"
                ]
            ),
            "Draw F1": (
                calibrated_results[
                    "Draw F1"
                ]
            ),
        })

    # ========================================================
    # COMPARISON
    # ========================================================

    results.insert(
        0,
        {
            "Model": "RF V3 Baseline",
            "Accuracy": (
                baseline_results[
                    "Accuracy"
                ]
            ),
            "Log Loss": (
                baseline_results[
                    "Log Loss"
                ]
            ),
            "Macro F1": (
                baseline_results[
                    "Macro F1"
                ]
            ),
            "Draw Recall": (
                baseline_results[
                    "Draw Recall"
                ]
            ),
            "Draw F1": (
                baseline_results[
                    "Draw F1"
                ]
            ),
        }
    )

    results_df = pd.DataFrame(
        results
    )

    # --------------------------------------------------------
    # Sort by Log Loss
    #
    # Lower is better for probability quality.
    # --------------------------------------------------------

    results_df = results_df.sort_values(
        "Log Loss",
        ascending=True,
    )

    print("\n")
    print("=" * 110)
    print("CALIBRATION COMPARISON")
    print("=" * 110)

    print(
        results_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    output_file = (
        MODEL_FILE.parent
        / "calibration_comparison.csv"
    )

    results_df.to_csv(
        output_file,
        index=False,
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