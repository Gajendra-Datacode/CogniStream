from pathlib import Path
import polars as pl


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "activity_events.csv"


def process_activity_data():
    print("Starting CogniStream data pipeline...")

    # Check if the source file exists
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

    # Read CSV data using Polars
    df = pl.read_csv(DATA_FILE)

    print(f"Total records loaded: {df.height}")
    print(f"Columns: {df.columns}")

    # Validate required columns
    required_columns = [
        "developer_id",
        "event_type",
        "timestamp",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Remove rows with missing essential data
    df = df.drop_nulls(
        subset=["developer_id", "event_type", "timestamp"]
    )

    # Remove duplicate records
    df = df.unique()

    # Sort activity by developer and timestamp
    df = df.sort(["developer_id", "timestamp"])

    print("Data validation successful!")
    print(f"Clean records: {df.height}")

    # Developer-wise event summary
    summary = df.group_by("developer_id").agg(
        pl.len().alias("total_events")
    ).sort("developer_id")

    print("\nDeveloper Activity Summary:")
    print(summary)

    print("\nCogniStream data processing completed!")

    return {
    "clean_records": df.height,
    "developer_summary": summary.to_dicts()
}


if __name__ == "__main__":
    process_activity_data()