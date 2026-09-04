from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

DATA_PATH = Path("ml/data/processed/training_features_v2.csv")
MODEL_PATH = Path("ml/models/random_forest_v2.pkl")

TEST_SEASON = "2025_26"


def main():

    print("Loading V2 feature dataset...")

    df = pd.read_csv(DATA_PATH)

    print(f"Loaded {len(df)} matches.")

    # --------------------------------------------------
    # Remove non-feature columns
    # --------------------------------------------------

    excluded_columns = [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTR",
        "Season"
    ]

    feature_columns = [
        col for col in df.columns
        if col not in excluded_columns
    ]

    X = df[feature_columns]
    y = df["FTR"]

    # --------------------------------------------------
    # Time-based train/test split
    # --------------------------------------------------

    train_df = df[df["Season"] != TEST_SEASON]
    test_df = df[df["Season"] == TEST_SEASON]

    X_train = train_df[feature_columns]
    y_train = train_df["FTR"]

    X_test = test_df[feature_columns]
    y_test = test_df["FTR"]

    print(f"\nTraining matches: {len(X_train)}")
    print(f"Testing matches: {len(X_test)}")

    # --------------------------------------------------
    # Random Forest
    # --------------------------------------------------

    print("\nTraining Random Forest V2...")

    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=10,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    print("Training complete.")

    # --------------------------------------------------
    # Evaluation
    # --------------------------------------------------

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print(f"\nAccuracy: {accuracy:.4f}")

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "Away Win",
                "Draw",
                "Home Win"
            ]
        )
    )

    print("\nConfusion Matrix:")

    print(confusion_matrix(y_test, predictions))

    # --------------------------------------------------
    # Feature importance
    # --------------------------------------------------

    importance = pd.DataFrame({
        "feature": feature_columns,
        "importance": model.feature_importances_
    })

    importance = importance.sort_values(
        "importance",
        ascending=False
    )

    print("\nTop 15 Features:")

    print(importance.head(15).to_string(index=False))

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(model, MODEL_PATH)

    print("\nModel saved to:")
    print(MODEL_PATH.resolve())


if __name__ == "__main__":
    main()