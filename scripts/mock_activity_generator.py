
import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Mock developer activity
developers = ["DEV001", "DEV002", "DEV003"]
event_types = ["coding", "commit", "slack_message", "ci_alert"]

events = []
start_time = datetime.now(timezone.utc) - timedelta(hours=8)

for developer in developers:
    current_time = start_time

    for _ in range(30):
        event_type = random.choice(event_types)

        event = {
            "developer_id": developer,
            "event_type": event_type,
            "timestamp": current_time.isoformat(),
            "source": {
                "coding": "vscode",
                "commit": "github",
                "slack_message": "slack",
                "ci_alert": "slack"
            }[event_type]
        }

        events.append(event)
        current_time += timedelta(minutes=random.randint(2, 15))

# Sort events by timestamp
events.sort(key=lambda x: x["timestamp"])

# Save JSON data
json_file = DATA_DIR / "activity_events.json"
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(events, f, indent=2)

# Save CSV data
csv_file = DATA_DIR / "activity_events.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["developer_id", "event_type", "timestamp", "source"]
    )
    writer.writeheader()
    writer.writerows(events)

print(f"Success! Generated {len(events)} events.")
print(f"JSON file: {json_file}")
print(f"CSV file: {csv_file}")
