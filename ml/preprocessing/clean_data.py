from pathlib import Path

import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "ml" / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "ml" / "data" / "processed"

OUTPUT_FILE = PROCESSED_DATA_DIR / "epl_matches.csv"


# --------------------------------------------------
# Columns we want to keep
# --------------------------------------------------

REQUIRED_COLUMNS = [
    "Div",
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
    "HS",
    "AS",
    "HST",
    "AST",
    "HF",
    "AF",
    "HC",
    "AC",
    "HY",
    "AY",
    "HR",
    "AR",

    # Bookmaker odds
    "B365H",
    "B365D",
    "B365A",
    "AvgH",
    "AvgD",
    "AvgA",
]


# --------------------------------------------------
# Load one season
# --------------------------------------------------

def load_season(file_path: Path) -> pd.DataFrame:
    """Load and clean a single EPL season CSV."""

    print(f"Loading: {file_path.name}")

    df = pd.read_csv(file_path)

    # Keep only columns that exist in the file
    available_columns = [
        column for column in REQUIRED_COLUMNS
        if column in df.columns
    ]

    df = df[available_columns].copy()

    # Add season from filename
    season = file_path.stem.replace("E0_", "")
    df["Season"] = season

    return df


# --------------------------------------------------
# Clean combined dataset
# --------------------------------------------------

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize the combined EPL dataset."""

    # Convert date
    df["Date"] = pd.to_datetime(
        df["Date"],
        dayfirst=True,
        errors="coerce"
    )

    # Remove rows with invalid essential information
    essential_columns = [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "FTHG",
        "FTAG",
        "FTR",
    ]

    df = df.dropna(subset=essential_columns)

    # Convert numerical columns
    numeric_columns = [
        "FTHG",
        "FTAG",
        "HS",
        "AS",
        "HST",
        "AST",
        "HF",
        "AF",
        "HC",
        "AC",
        "HY",
        "AY",
        "HR",
        "AR",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Normalize result values
    df["FTR"] = df["FTR"].str.upper().str.strip()

    # Remove invalid results
    df = df[df["FTR"].isin(["H", "D", "A"])]

    # Clean team names
    df["HomeTeam"] = df["HomeTeam"].str.strip()
    df["AwayTeam"] = df["AwayTeam"].str.strip()

    # Sort chronologically
    df = df.sort_values(
        by=["Date", "HomeTeam", "AwayTeam"]
    ).reset_index(drop=True)

    return df


# --------------------------------------------------
# Main pipeline
# --------------------------------------------------

def main():

    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Only use completed seasons for training dataset.
    # 2026/27 is the current season and is excluded.
    season_files = sorted(
        RAW_DATA_DIR.glob("E0_*.csv")
    )

    season_files = [
        file for file in season_files
        if file.stem != "E0_2026_27"
    ]

    if not season_files:
        raise FileNotFoundError(
            "No EPL CSV files found in ml/data/raw/"
        )

    print(f"\nFound {len(season_files)} season files.\n")

    # Load all seasons
    dataframes = [
        load_season(file)
        for file in season_files
    ]

    # Combine
    combined_df = pd.concat(
        dataframes,
        ignore_index=True
    )

    print(
        f"\nCombined rows before cleaning: "
        f"{len(combined_df)}"
    )

    # Clean
    combined_df = clean_data(combined_df)

    print(
        f"Rows after cleaning: "
        f"{len(combined_df)}"
    )

    # Save
    combined_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"\nProcessed dataset saved to:\n"
        f"{OUTPUT_FILE}"
    )

    print(
        f"\nFinal shape: "
        f"{combined_df.shape}"
    )

    print("\nColumns:")
    print(combined_df.columns.tolist())


if __name__ == "__main__":
    main()