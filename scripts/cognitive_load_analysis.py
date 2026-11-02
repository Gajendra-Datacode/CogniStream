
import polars as pl
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "activity_events.csv"
OUTPUT_FILE = BASE_DIR / "data" / "cognitive_load_summary.csv"

# Load activity data
df = pl.read_csv(DATA_FILE)

# Define event categories
focus_events = ["coding", "commit"]
interruption_events = ["slack_message", "ci_alert"]

# Calculate developer-wise metrics
summary = (
    df.group_by("developer_id")
    .agg([
        pl.len().alias("total_events"),

        pl.col("event_type")
        .is_in(focus_events)
        .sum()
        .alias("focus_events"),

        pl.col("event_type")
        .is_in(interruption_events)
        .sum()
        .alias("interruption_events")
    ])
    .with_columns([
        (
            pl.col("focus_events") /
            pl.col("total_events") * 100
        ).round(2).alias("focus_percentage"),

        (
            pl.col("interruption_events") /
            pl.col("total_events") * 100
        ).round(2).alias("interruption_percentage")
    ])
    .sort("developer_id")
)

# Save results
summary.write_csv(OUTPUT_FILE)

# Display results
print("\n========== COGNITIVE LOAD ANALYSIS ==========")

print(summary)

print("\n========== ANALYSIS COMPLETED ==========")

print(f"Report saved: {OUTPUT_FILE}")
