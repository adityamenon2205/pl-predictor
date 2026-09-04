from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
)
from xgboost import XGBClassifier

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

COMPARISON_PATH = (
    MODEL_DIR
    / "model_comparison_v4.csv"
)

TEST_SEASON = "2025_26"


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
print("V4 MODEL TRAINING")
print("=" * 70)

print("\nLoading V4 dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")


# ============================================================
# VALIDATE DATA
# ============================================================

if "FTR" not in df.columns:
    raise ValueError("Target column FTR not found.")

if "Season" not in df.columns:
    raise ValueError("Season column not found.")

if TEST_SEASON not in df["Season"].values:
    raise ValueError(
        f"Test season {TEST_SEASON} not found."
    )


# ------------------------------------------------------------
# Check 2026/27
# ------------------------------------------------------------

if "2026_27" in df["Season"].values:

    raise ValueError(
        "2026/27 data is present. "
        "It must not be used for training."
    )


# ============================================================
# DEFINE MODEL FEATURES
# ============================================================

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
    f"\nNumber of model features: "
    f"{len(feature_columns)}"
)


# ------------------------------------------------------------
# Check feature values
# ------------------------------------------------------------

X_all = df[feature_columns]

if X_all.isna().any().any():

    missing = X_all.isna().sum()

    missing = missing[
        missing > 0
    ]

    print("\nMissing feature values:")
    print(missing)

    raise ValueError(
        "Missing values found in model features."
    )


if np.isinf(
    X_all.select_dtypes(
        include=np.number
    ).values
).any():

    raise ValueError(
        "Infinite values found in model features."
    )


# ============================================================
# TIME-BASED TRAIN / TEST SPLIT
# ============================================================

print("\n" + "=" * 70)
print("TIME-BASED TRAIN / TEST SPLIT")
print("=" * 70)


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

print(
    f"Test season: "
    f"{TEST_SEASON}"
)


X_train = train_df[
    feature_columns
]

X_test = test_df[
    feature_columns
]


y_train = (
    train_df["FTR"]
    .map(LABEL_TO_INT)
    .values
)

y_test = (
    test_df["FTR"]
    .map(LABEL_TO_INT)
    .values
)


# ============================================================
# CHECK TARGETS
# ============================================================

if np.isnan(y_train).any():
    raise ValueError(
        "Unknown target values found in training data."
    )

if np.isnan(y_test).any():
    raise ValueError(
        "Unknown target values found in test data."
    )


print("\nTraining target distribution:")

train_target_counts = (
    train_df["FTR"]
    .value_counts()
    .reindex(["H", "D", "A"])
)

print(
    train_target_counts.to_string()
)


print("\nTest target distribution:")

test_target_counts = (
    test_df["FTR"]
    .value_counts()
    .reindex(["H", "D", "A"])
)

print(
    test_target_counts.to_string()
)


# ============================================================
# MODEL DEFINITIONS
# ============================================================

models = {

    "Random Forest V4": RandomForestClassifier(
        n_estimators=500,
        max_depth=None,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight=None,
        random_state=42,
        n_jobs=-1
    ),

    "XGBoost V4": XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1
    ),

    "XGBoost V4 Balanced": XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1
    )
}


# ============================================================
# CLASS WEIGHTS FOR BALANCED MODEL
# ============================================================

class_counts = np.bincount(
    y_train,
    minlength=3
)

total_samples = len(y_train)

class_weights = {
    class_index:
        total_samples
        / (
            3
            * class_counts[class_index]
        )
    for class_index in range(3)
}


print("\nClass weights:")

for class_index in range(3):

    print(
        f"  {INT_TO_LABEL[class_index]}: "
        f"{class_weights[class_index]:.4f}"
    )


# ------------------------------------------------------------
# XGBoost does not support class_weight directly.
# Calculate sample weights.
# ------------------------------------------------------------

sample_weights = np.array([
    class_weights[label]
    for label in y_train
])


# ============================================================
# TRAIN MODELS
# ============================================================

results = []


for model_name, model in models.items():

    print("\n" + "=" * 70)

    print(
        f"TRAINING: {model_name}"
    )

    print("=" * 70)

    # --------------------------------------------------------
    # Apply sample weights only to balanced XGBoost
    # --------------------------------------------------------

    if model_name == "XGBoost V4 Balanced":

        model.fit(
            X_train,
            y_train,
            sample_weight=sample_weights
        )

    else:

        model.fit(
            X_train,
            y_train
        )


    # ========================================================
    # PREDICTIONS
    # ========================================================

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )


    # --------------------------------------------------------
    # Normalize probability order
    # --------------------------------------------------------

    normalized_probabilities = np.zeros(
        (len(probabilities), 3)
    )


    for i, class_value in enumerate(
        model.classes_
    ):

        if isinstance(
            class_value,
            str
        ):

            label = class_value

        else:

            label = INT_TO_LABEL[
                int(class_value)
            ]

        normalized_probabilities[
            :,
            LABEL_TO_INT[label]
        ] = probabilities[:, i]


    probabilities = (
        normalized_probabilities
    )


    # --------------------------------------------------------
    # Predictions may be encoded integers
    # --------------------------------------------------------

    if predictions.dtype.kind in "OUS":

        predictions = np.array([
            LABEL_TO_INT[prediction]
            for prediction in predictions
        ])

    else:

        predictions = predictions.astype(int)


    # ========================================================
    # METRICS
    # ========================================================

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0
    )

    logloss = log_loss(
        y_test,
        probabilities,
        labels=[0, 1, 2]
    )


    report = classification_report(
        y_test,
        predictions,
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
    # PRINT RESULTS
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
            y_test,
            predictions,
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
        y_test,
        predictions,
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


    print("Confusion Matrix:")

    print(
        cm_df.to_string()
    )


    # ========================================================
    # PROBABILITY SUMMARY
    # ========================================================

    print("\nAverage predicted probabilities:")

    print(
        f"  Away : "
        f"{probabilities[:, 0].mean():.4f}"
    )

    print(
        f"  Draw : "
        f"{probabilities[:, 1].mean():.4f}"
    )

    print(
        f"  Home : "
        f"{probabilities[:, 2].mean():.4f}"
    )


    # ========================================================
    # DRAW PERFORMANCE
    # ========================================================

    draw_f1 = report[
        "Draw"
    ]["f1-score"]

    draw_precision = report[
        "Draw"
    ]["precision"]

    draw_recall = report[
        "Draw"
    ]["recall"]


    print("\nDraw performance:")

    print(
        f"  Precision : "
        f"{draw_precision:.4f}"
    )

    print(
        f"  Recall    : "
        f"{draw_recall:.4f}"
    )

    print(
        f"  F1        : "
        f"{draw_f1:.4f}"
    )


    # ========================================================
    # FEATURE IMPORTANCE
    # ========================================================

    if hasattr(
        model,
        "feature_importances_"
    ):

        importance_df = pd.DataFrame({

            "feature":
                feature_columns,

            "importance":
                model.feature_importances_

        })

        importance_df = (
            importance_df
            .sort_values(
                "importance",
                ascending=False
            )
        )

        print(
            "\nTop 20 features:"
        )

        print(
            importance_df
            .head(20)
            .to_string(
                index=False
            )
        )


    # ========================================================
    # SAVE MODEL
    # ========================================================

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    if model_name == "Random Forest V4":

        model_filename = (
            "random_forest_v4.pkl"
        )

    elif model_name == "XGBoost V4":

        model_filename = (
            "xgboost_v4.pkl"
        )

    else:

        model_filename = (
            "xgboost_v4_balanced.pkl"
        )


    model_path = (
        MODEL_DIR
        / model_filename
    )


    # --------------------------------------------------------
    # Save bundle with exact feature list
    # --------------------------------------------------------

    bundle = {

        "model": model,

        "features": feature_columns,

        "label_mapping": LABEL_TO_INT

    }


    joblib.dump(
        bundle,
        model_path
    )


    print(
        "\n✓ Model saved:"
    )

    print(
        f"  {model_path}"
    )


    # ========================================================
    # STORE COMPARISON RESULTS
    # ========================================================

    results.append({

        "model":
            model_name,

        "accuracy":
            accuracy,

        "log_loss":
            logloss,

        "macro_f1":
            macro_f1,

        "away_precision":
            report["Away"]["precision"],

        "away_recall":
            report["Away"]["recall"],

        "away_f1":
            report["Away"]["f1-score"],

        "draw_precision":
            draw_precision,

        "draw_recall":
            draw_recall,

        "draw_f1":
            draw_f1,

        "home_precision":
            report["Home"]["precision"],

        "home_recall":
            report["Home"]["recall"],

        "home_f1":
            report["Home"]["f1-score"],

        "avg_p_away":
            probabilities[:, 0].mean(),

        "avg_p_draw":
            probabilities[:, 1].mean(),

        "avg_p_home":
            probabilities[:, 2].mean()

    })


# ============================================================
# MODEL COMPARISON
# ============================================================

comparison_df = pd.DataFrame(
    results
)


comparison_df = (
    comparison_df
    .sort_values(
        "log_loss"
    )
)


print("\n" + "=" * 70)
print("V4 MODEL COMPARISON")
print("=" * 70)


print(
    comparison_df
    .round(4)
    .to_string(index=False)
)


# ============================================================
# SAVE COMPARISON
# ============================================================

comparison_df.to_csv(
    COMPARISON_PATH,
    index=False
)


print(
    "\n✓ Comparison saved:"
)

print(
    f"  {COMPARISON_PATH}"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("V4 TRAINING COMPLETE")
print("=" * 70)

best_accuracy = comparison_df.loc[
    comparison_df["accuracy"].idxmax()
]

best_logloss = comparison_df.loc[
    comparison_df["log_loss"].idxmin()
]

best_macro_f1 = comparison_df.loc[
    comparison_df["macro_f1"].idxmax()
]

best_draw_f1 = comparison_df.loc[
    comparison_df["draw_f1"].idxmax()
]


print(
    f"""
Best Accuracy:
    {best_accuracy['model']}
    {best_accuracy['accuracy']:.4f}

Best Log Loss:
    {best_logloss['model']}
    {best_logloss['log_loss']:.4f}

Best Macro F1:
    {best_macro_f1['model']}
    {best_macro_f1['macro_f1']:.4f}

Best Draw F1:
    {best_draw_f1['model']}
    {best_draw_f1['draw_f1']:.4f}
"""
)

print("=" * 70)