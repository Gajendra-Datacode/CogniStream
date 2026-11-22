from pathlib import Path
import os

import polars as pl
import clickhouse_connect


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "activity_events.csv"


# ClickHouse configuration
CLICKHOUSE_DATABASE = "cognistream"
CLICKHOUSE_TABLE = "activity_events"


def process_activity_data():
    print("Starting CogniStream data pipeline...")

    # 1. Check source file
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

    # 2. Read CSV using Polars
    df = pl.read_csv(DATA_FILE)

    print(f"Total records loaded: {df.height}")
    print(f"Columns: {df.columns}")

    # 3. Validate required columns
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

    # 4. Add source column if it does not exist
    if "source" not in df.columns:
        df = df.with_columns(
            pl.lit("csv").alias("source")
        )

    # 5. Convert timestamp to UTC datetime
    df = df.with_columns(
        pl.col("timestamp")
        .cast(pl.String)
        .str.to_datetime(
            time_zone="UTC",
            time_unit="ms",
            strict=False
        )
    )

    # 6. Remove rows with missing essential data
    df = df.drop_nulls(
        subset=[
            "developer_id",
            "event_type",
            "timestamp",
            "source",
        ]
    )

    # 7. Remove duplicate records
    df = df.unique(
        subset=[
            "developer_id",
            "event_type",
            "timestamp",
            "source",
        ]
    )

    # 8. Sort data
    df = df.sort(["developer_id", "timestamp"])

    print("Data validation successful!")
    print(f"Clean records: {df.height}")

    # 9. Developer-wise summary
    summary = (
        df.group_by("developer_id")
        .agg(pl.len().alias("total_events"))
        .sort("developer_id")
    )

    print("\nDeveloper Activity Summary:")
    print(summary)

    # 10. Connect to ClickHouse
    print("\nConnecting to ClickHouse...")

    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER"),
        password=os.getenv("CLICKHOUSE_PASSWORD"),
    )

    print("ClickHouse connection successful!")

    # 11. Fetch existing records to prevent duplicates
    existing_records = client.query(
        f"""
        SELECT developer_id, event_type, timestamp, source
        FROM {CLICKHOUSE_DATABASE}.{CLICKHOUSE_TABLE}
        """
    ).result_rows

    def normalize_timestamp(value):
        # Normalize all timestamps to UTC-aware datetimes
        if value.tzinfo is None:
            from datetime import timezone
            return value.replace(tzinfo=timezone.utc)

        from datetime import timezone
        return value.astimezone(timezone.utc)

    existing_keys = {
        (
            developer_id,
            event_type,
            normalize_timestamp(timestamp),
            source,
        )
        for developer_id, event_type, timestamp, source
        in existing_records
    }

    # 12. Find only new records
    new_records = []

    for row in df.to_dicts():
        record = (
            row["developer_id"],
            row["event_type"],
            normalize_timestamp(row["timestamp"]),
            row["source"],
        )

        if record not in existing_keys:
            new_records.append(record)
            existing_keys.add(record)

    print(f"New records to insert: {len(new_records)}")

    # 13. Insert new records into ClickHouse
    if new_records:
        client.insert(
            CLICKHOUSE_TABLE,
            new_records,
            column_names=[
                "developer_id",
                "event_type",
                "timestamp",
                "source",
            ],
            database=CLICKHOUSE_DATABASE,
        )

        print("Data inserted successfully!")

    else:
        print("No new records found. Skipping insertion.")

    # 14. Verify database record count
    total_records = client.query(
        f"""
        SELECT count()
        FROM {CLICKHOUSE_DATABASE}.{CLICKHOUSE_TABLE}
        """
    ).result_rows[0][0]

    client.close()

    print(f"Total records in ClickHouse: {total_records}")
    print("\nCogniStream pipeline completed successfully!")

    # 15. Return Airflow-compatible result
    return {
        "clean_records": df.height,
        "new_records_inserted": len(new_records),
        "total_clickhouse_records": total_records,
        "developer_summary": summary.to_dicts(),
    }


if __name__ == "__main__":
    process_activity_data()