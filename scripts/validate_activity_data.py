
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "activity_events.json"

if not DATA_FILE.exists():
    raise FileNotFoundError(
        "Activity data not found. Run mock_activity_generator.py first."
    )

with open(DATA_FILE, "r", encoding="utf-8") as file:
    events = json.load(file)

required_fields = {
    "developer_id",
    "event_type",
    "timestamp",
    "source"
}

errors = []

for row_number, event in enumerate(events, start=1):
    missing = required_fields - event.keys()

    if missing:
        errors.append(
            f"Row {row_number}: missing fields {sorted(missing)}"
        )

print(f"Total events: {len(events)}")
print(f"Unique developers: {len(set(e['developer_id'] for e in events))}")

print("\nEvents by type:")
for event_type, count in Counter(
    e["event_type"] for e in events
).items():
    print(f"{event_type}: {count}")

if errors:
    print("\nValidation failed:")
    for error in errors:
        print(error)
else:
    print("\nValidation successful! All events have required fields.")
