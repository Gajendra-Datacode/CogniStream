
import polars as pl
from pathlib import Path

# Locate project data
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "activity_events.csv"

# Load CSV
df = pl.read_csv(DATA_FILE)

print("\n========== COGNISTREAM ANALYTICS ==========")

# 1. Total events
print("\n1. Total Activity Events:")
print(df.height)

# 2. Developer-wise activity
print("\n2. Developer Activity:")
developer_summary = (
    df.group_by("developer_id")
    .agg(pl.len().alias("total_events"))
    .sort("developer_id")
)
print(developer_summary)

# 3. Event type analysis
print("\n3. Event Type Analysis:")
event_summary = (
    df.group_by("event_type")
    .agg(pl.len().alias("total_events"))
    .sort("total_events", descending=True)
)
print(event_summary)

# 4. Source-wise analysis
print("\n4. Activity by Source:")
source_summary = (
    df.group_by("source")
    .agg(pl.len().alias("total_events"))
    .sort("total_events", descending=True)
)
print(source_summary)

# 5. Save developer summary
OUTPUT_FILE = BASE_DIR / "data" / "developer_summary.csv"
developer_summary.write_csv(OUTPUT_FILE)

print(f"\nSummary saved to: {OUTPUT_FILE}")
print("\n========== ANALYSIS COMPLETED ==========")
