
from fastapi import FastAPI
from pathlib import Path
import polars as pl

# ==========================================
# 1. FASTAPI CONFIGURATION
# ==========================================

app = FastAPI(
    title="CogniStream API",
    description="Developer Activity, Flow-State and Cognitive Load Analytics",
    version="1.1.0"
)

# ==========================================
# 2. PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "activity_events.csv"

COGNITIVE_LOAD_FILE = (
    BASE_DIR / "data" / "cognitive_load_summary.csv"
)

FLOW_SESSIONS_FILE = (
    BASE_DIR / "data" / "flow_sessions.csv"
)


# ==========================================
# 3. HOME ENDPOINT
# ==========================================

@app.get("/")
def home():
    return {
        "project": "CogniStream",
        "message": "Developer Analytics API is running!",
        "status": "active"
    }


# ==========================================
# 4. HEALTH CHECK
# ==========================================

@app.get("/health")
def health():
    return {"status": "healthy"}


# ==========================================
# 5. DEVELOPER ANALYTICS
# ==========================================

@app.get("/developers")
def get_developers():

    if not DATA_FILE.exists():
        return {"error": "Activity data file not found"}

    df = pl.read_csv(DATA_FILE)

    developers = (
        df.group_by("developer_id")
        .agg(
            pl.len().alias("total_events")
        )
        .sort("developer_id")
    )

    return developers.to_dicts()


# ==========================================
# 6. EVENT SUMMARY
# ==========================================

@app.get("/event-summary")
def event_summary():

    if not DATA_FILE.exists():
        return {"error": "Activity data file not found"}

    df = pl.read_csv(DATA_FILE)

    summary = (
        df.group_by("event_type")
        .agg(
            pl.len().alias("total_events")
        )
        .sort("event_type")
    )

    return summary.to_dicts()


# ==========================================
# 7. RECENT ACTIVITY
# ==========================================

@app.get("/activity")
def get_activity():

    if not DATA_FILE.exists():
        return {"error": "Activity data file not found"}

    df = pl.read_csv(DATA_FILE)

    return {
        "total_events": df.height,
        "events": df.head(20).to_dicts()
    }


# ==========================================
# 8. COGNITIVE LOAD ANALYSIS
# ==========================================

@app.get("/cognitive-load")
def get_cognitive_load():

    if not COGNITIVE_LOAD_FILE.exists():
        return {"error": "Cognitive load report not found"}

    df = pl.read_csv(COGNITIVE_LOAD_FILE)

    return {
        "total_developers": df.height,
        "cognitive_load": df.to_dicts()
    }


# ==========================================
# 9. FLOW-STATE ANALYSIS
# ==========================================

@app.get("/flow-sessions")
def get_flow_sessions():

    if not FLOW_SESSIONS_FILE.exists():
        return {"error": "Flow sessions report not found"}

    df = pl.read_csv(FLOW_SESSIONS_FILE)

    return {
        "total_sessions": df.height,
        "flow_sessions": df.to_dicts()
    }
