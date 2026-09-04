from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from xgboost import XGBClassifier

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "training_features_v2.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
)

MODEL_FILE = MODEL_DIR / "xgboost_v2.pkl"


# --------------------------------------------------
# Configuration
# --------------------------------------------------

TEST_SEASON = "2025_26"


# --------------------------------------------------
# Load data
# --------------------------------------------------

def load_data():

    df = pd.read_csv(
        DATA_FILE,
        parse_dates=["Date"]
    )

    print(f"Loaded {len(df)} matches.")

    return df


# --------------------------------------------------
# Prepare data
# --------------------------------------------------

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


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    df = load_data()

    # ------------------------------------------------
    # Time-based split
    # ------------------------------------------------

    train_df = df[
        df["Season"] != TEST_SEASON
    ].copy()

    test_df = df[
        df["Season"] == TEST_SEASON
    ].copy()

    print(
        f"\nTraining matches: {len(train_df)}"
    )

    print(
        f"Testing matches: {len(test_df)}"
    )

    # ------------------------------------------------
    # Prepare features
    # ------------------------------------------------

    X_train, y_train, feature_columns = prepare_data(
        train_df
    )

    X_test, y_test, _ = prepare_data(
        test_df
    )

    # ------------------------------------------------
    # Encode target
    # ------------------------------------------------

    label_mapping = {
        "A": 0,
        "D": 1,
        "H": 2,
    }

    y_train_encoded = y_train.map(
        label_mapping
    )

    y_test_encoded = y_test.map(
        label_mapping
    )

    # ------------------------------------------------
    # XGBoost
    # ------------------------------------------------

    print("\nTraining XGBoost...")

    model = XGBClassifier(
        n_estimators=500,
        max_depth=5,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train_encoded
    )

    print("Training complete.")

    # ------------------------------------------------
    # Predictions
    # ------------------------------------------------

    predictions_encoded = model.predict(
        X_test
    )

    predictions = pd.Series(
        predictions_encoded
    ).map({
        0: "A",
        1: "D",
        2: "H",
    })

    # ------------------------------------------------
    # Evaluation
    # ------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(
        f"\nAccuracy: {accuracy:.4f}"
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

    print("\nConfusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            predictions,
            labels=["H", "D", "A"],
        )
    )

    # ------------------------------------------------
    # Feature importance
    # ------------------------------------------------

    importance = pd.DataFrame({
        "feature": feature_columns,
        "importance": model.feature_importances_,
    })

    importance = importance.sort_values(
        "importance",
        ascending=False
    )

    print("\nTop 10 Features:")

    print(
        importance.head(10).to_string(
            index=False
        )
    )

    # ------------------------------------------------
    # Save
    # ------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "model": model,
            "features": feature_columns,
            "label_mapping": label_mapping,
        },
        MODEL_FILE,
    )

    print(
        f"\nModel saved to:\n{MODEL_FILE}"
    )


if __name__ == "__main__":
    main()