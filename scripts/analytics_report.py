from pathlib import Path
import polars as pl
import clickhouse_connect
import os


def generate_analytics_report():

    print("Starting CogniStream Analytics Report...")

    # Connect to ClickHouse
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER"),
        password=os.getenv("CLICKHOUSE_PASSWORD"),
    )

    # Fetch activity data
    query = """
        SELECT
            developer_id,
            event_type,
            timestamp,
            source
        FROM cognistream.activity_events
    """

    result = client.query(query)

    # Convert ClickHouse data to Polars DataFrame
    df = pl.DataFrame(
        result.result_rows,
        schema=[
            "developer_id",
            "event_type",
            "timestamp",
            "source",
        ],
        orient="row",
    )

    print(f"Total records analyzed: {df.height}")

    # Developer activity report
    developer_report = (
        df.group_by("developer_id")
        .agg([
            pl.len().alias("total_events"),
            pl.col("event_type")
            .n_unique()
            .alias("unique_event_types"),
        ])
        .sort("developer_id")
    )

    print("\nDeveloper Analytics Report:")
    print(developer_report)

    # Event type report
    event_report = (
        df.group_by("event_type")
        .agg(pl.len().alias("total_events"))
        .sort("total_events", descending=True)
    )

    print("\nEvent Type Report:")
    print(event_report)

    # Save reports
    output_dir = Path("/opt/airflow/data/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    developer_report.write_csv(
        output_dir / "developer_analytics_report.csv"
    )

    event_report.write_csv(
        output_dir / "event_analytics_report.csv"
    )

    client.close()

    print("\nReports generated successfully!")

    return {
        "total_records": df.height,
        "developers": developer_report.to_dicts(),
        "event_types": event_report.to_dicts(),
    }


if __name__ == "__main__":
    generate_analytics_report()