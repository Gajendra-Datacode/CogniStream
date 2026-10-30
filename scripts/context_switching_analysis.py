
import polars as pl
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "activity_events.csv"
OUTPUT_FILE = BASE_DIR / "data" / "context_switching_summary.csv"

# Load activity data
df = pl.read_csv(DATA_FILE)

# Sort events by developer and timestamp
df = df.sort(["developer_id", "timestamp"])

# Define event categories
focus_events = ["coding", "commit"]
interruption_events = ["slack_message", "ci_alert"]

# Identify event categories
df = df.with_columns(
    pl.when(pl.col("event_type").is_in(focus_events))
    .then(pl.lit("focus"))
    .when(pl.col("event_type").is_in(interruption_events))
    .then(pl.lit("interruption"))
    .otherwise(pl.lit("other"))
    .alias("activity_category")
)

# Calculate interruption counts
interruption_summary = (
    df.filter(
        pl.col("event_type").is_in(interruption_events)
    )
    .group_by(["developer_id", "event_type"])
    .agg(
        pl.len().alias("interruption_count")
    )
)

# Calculate consecutive activity transitions
df = df.with_columns(
    pl.col("activity_category")
    .shift(1)
    .over("developer_id")
    .alias("previous_activity")
)

switches = df.filter(
    (pl.col("previous_activity") == "focus")
    & (pl.col("activity_category") == "interruption")
)

switch_summary = (
    switches.group_by("developer_id")
    .agg(
        pl.len().alias("focus_to_interruption_switches")
    )
)

# Total interruption summary
total_summary = (
    df.filter(
        pl.col("activity_category") == "interruption"
    )
    .group_by("developer_id")
    .agg(
        pl.len().alias("total_interruptions")
    )
)

# Combine reports
report = (
    total_summary
    .join(switch_summary, on="developer_id", how="left")
    .with_columns(
        pl.col("focus_to_interruption_switches").fill_null(0)
    )
    .sort("developer_id")
)

# Save report
report.write_csv(OUTPUT_FILE)

# Display results
print("\n========== COGNISTREAM CONTEXT SWITCHING ==========")

print("\nInterruption Counts:")
print(interruption_summary.sort("developer_id"))

print("\nDeveloper Context Switching Report:")
print(report)

print(f"\nReport saved to: {OUTPUT_FILE}")

print("\n========== ANALYSIS COMPLETED ==========")
 