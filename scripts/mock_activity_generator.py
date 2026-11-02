
import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ==========================================
# 1. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

random.seed(42)

developers = ["DEV001", "DEV002", "DEV003"]

events = []

start_time = datetime.now(timezone.utc) - timedelta(hours=8)


# ==========================================
# 2. EVENT GENERATOR
# ==========================================

def add_event(developer, event_type, timestamp):

    event = {
        "developer_id": developer,
        "event_type": event_type,
        "timestamp": timestamp.isoformat(),
        "source": {
            "coding": "vscode",
            "commit": "github",
            "slack_message": "slack",
            "ci_alert": "slack"
        }[event_type]
    }

    events.append(event)


# ==========================================
# 3. GENERATE DEVELOPER SESSIONS
# ==========================================

for developer in developers:

    current_time = start_time

    # Each developer gets a long coding session
    session_duration = random.randint(90, 120)

    session_end = current_time + timedelta(
        minutes=session_duration
    )

    # Coding events every 5-10 minutes
    while current_time <= session_end:

        add_event(
            developer,
            "coding",
            current_time
        )

        # Occasional commits
        if random.random() < 0.20:
            add_event(
                developer,
                "commit",
                current_time + timedelta(seconds=30)
            )

        current_time += timedelta(
            minutes=random.randint(5, 10)
        )

    # Add interruptions after the long session
    for _ in range(5):

        current_time += timedelta(
            minutes=random.randint(10, 20)
        )

        event_type = random.choice([
            "slack_message",
            "ci_alert"
        ])

        add_event(
            developer,
            event_type,
            current_time
        )

    # Add a few shorter coding sessions
    for _ in range(5):

        current_time += timedelta(
            minutes=random.randint(10, 20)
        )

        add_event(
            developer,
            random.choice(["coding", "commit"]),
            current_time
        )


# ==========================================
# 4. SORT EVENTS
# ==========================================

events.sort(
    key=lambda x: x["timestamp"]
)


# ==========================================
# 5. SAVE JSON
# ==========================================

json_file = DATA_DIR / "activity_events.json"

with open(json_file, "w", encoding="utf-8") as file:

    json.dump(
        events,
        file,
        indent=2
    )


# ==========================================
# 6. SAVE CSV
# ==========================================

csv_file = DATA_DIR / "activity_events.csv"

with open(
    csv_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "developer_id",
            "event_type",
            "timestamp",
            "source"
        ]
    )

    writer.writeheader()
    writer.writerows(events)


# ==========================================
# 7. COMPLETION
# ==========================================

print(f"Success! Generated {len(events)} events.")

print(f"JSON file: {json_file}")
print(f"CSV file: {csv_file}")

print("\nDeveloper event counts:")

for developer in developers:

    count = sum(
        1 for event in events
        if event["developer_id"] == developer
    )

    print(f"{developer}: {count} events")
