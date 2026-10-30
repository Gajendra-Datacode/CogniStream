
import polars as pl
from pathlib import Path
from datetime import datetime

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "activity_events.csv"
OUTPUT_FILE = BASE_DIR / "data" / "flow_sessions.csv"

# Load activity data
df = pl.read_csv(DATA_FILE)

df = df.with_columns(
    pl.col("timestamp").str.to_datetime(
        time_zone="UTC",
        strict=True
    )
).sort(["developer_id", "timestamp"])

# Events considered focus-related
FOCUS_EVENTS = {"coding", "commit"}

# Events that interrupt focus
INTERRUPTION_EVENTS = {"slack_message", "ci_alert"}

MAX_GAP_MINUTES = 15
MIN_FLOW_MINUTES = 90

sessions = []

for developer in df["developer_id"].unique().to_list():

    developer_events = (
        df.filter(pl.col("developer_id") == developer)
        .sort("timestamp")
        .to_dicts()
    )

    session_start = None
    session_end = None
    event_count = 0

    def save_session():
        if session_start is not None:
            duration = (
                session_end - session_start
            ).total_seconds() / 60

            sessions.append({
                "developer_id": developer,
                "start_time": session_start.isoformat(),
                "end_time": session_end.isoformat(),
                "duration_minutes": round(duration, 2),
                "focus_events": event_count,
                "qualified_90_min": duration >= MIN_FLOW_MINUTES
            })

    for event in developer_events:

        event_time = event["timestamp"]
        event_type = event["event_type"]

        if event_type in INTERRUPTION_EVENTS:
            save_session()
            session_start = None
            session_end = None
            event_count = 0

        elif event_type in FOCUS_EVENTS:

            if session_start is None:
                session_start = event_time
                session_end = event_time
                event_count = 1

            else:
                gap = (
                    event_time - session_end
                ).total_seconds() / 60

                if gap > MAX_GAP_MINUTES:
                    save_session()
                    session_start = event_time
                    session_end = event_time
                    event_count = 1
                else:
                    session_end = event_time
                    event_count += 1

    save_session()

# Convert results into Polars DataFrame
if sessions:
    result = pl.DataFrame(sessions)

    result.write_csv(OUTPUT_FILE)

    print("\n========== FLOW STATE ANALYSIS ==========")
    print(result)

    qualified = result.filter(
        pl.col("qualified_90_min") == True
    )

    print("\n90+ Minute Focus Sessions:")
    print(qualified)

    print(f"\nTotal focus sessions: {result.height}")
    print(f"90+ minute sessions: {qualified.height}")

    print(f"\nResults saved to: {OUTPUT_FILE}")

else:
    print("No focus sessions found.")

# Interruption summary
interruptions = (
    df.filter(pl.col("event_type").is_in(
        list(INTERRUPTION_EVENTS)
    ))
    .group_by(["developer_id", "event_type"])
    .agg(pl.len().alias("interruption_count"))
    .sort(["developer_id", "event_type"])
)

print("\n========== INTERRUPTION SUMMARY ==========")
print(interruptions)
