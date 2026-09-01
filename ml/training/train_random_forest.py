from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "ml"
    / "data"
    / "processed"
    / "training_features.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
)

MODEL_FILE = MODEL_DIR / "random_forest_model.pkl"


# --------------------------------------------------
# Configuration
# --------------------------------------------------

# Use the most recent completed season as test data.
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
# Prepare features
# --------------------------------------------------

def prepare_data(df):

    # Features that should NOT be given to the model
    excluded_columns = [
        "Date",
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
# Train
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
    # Prepare X / y
    # ------------------------------------------------

    X_train, y_train, feature_columns = prepare_data(
        train_df
    )

    X_test, y_test, _ = prepare_data(
        test_df
    )

    # ------------------------------------------------
    # Train Random Forest
    # ------------------------------------------------

    print("\nTraining Random Forest...")

    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train
    )

    print("Training complete.")

    # ------------------------------------------------
    # Predictions
    # ------------------------------------------------

    predictions = model.predict(
        X_test
    )

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
    # Save model
    # ------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "model": model,
            "features": feature_columns,
        },
        MODEL_FILE,
    )

    print(
        f"\nModel saved to:\n{MODEL_FILE}"
    )


if __name__ == "__main__":
    main()