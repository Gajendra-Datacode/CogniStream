
from fastapi import FastAPI
from pathlib import Path
import polars as pl

app = FastAPI(
    title="CogniStream API",
    description="Developer Activity and Flow-State Analytics",
    version="1.0.0"
)

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "activity_events.csv"


@app.get("/")
def home():
    return {
        "project": "CogniStream",
        "message": "Developer Analytics API is running!",
        "status": "active"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/developers")
def get_developers():

    if not DATA_FILE.exists():
        return {"error": "Activity data file not found"}

    df = pl.read_csv(DATA_FILE)

    developers = (
        df.group_by("developer_id")
        .agg(pl.len().alias("total_events"))
        .sort("developer_id")
    )

    return developers.to_dicts()


@app.get("/event-summary")
def event_summary():

    if not DATA_FILE.exists():
        return {"error": "Activity data file not found"}

    df = pl.read_csv(DATA_FILE)

    summary = (
        df.group_by("event_type")
        .agg(pl.len().alias("total_events"))
        .sort("event_type")
    )

    return summary.to_dicts()


@app.get("/activity")
def get_activity():

    if not DATA_FILE.exists():
        return {"error": "Activity data file not found"}

    df = pl.read_csv(DATA_FILE)

    return {
        "total_events": df.height,
        "events": df.head(20).to_dicts()
    }
