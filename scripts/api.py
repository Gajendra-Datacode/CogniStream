from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import polars as pl
from scripts.clickhouse_client import get_clickhouse_client

# ============================================
# 1. FASTAPI CONFIGURATION
# ============================================

app = FastAPI(
    title="CogniStream API",
    description="Developer Activity, Flow-State and Cognitive Load Analytics",
    version="1.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 2. PROJECT PATHS
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent
COGNITIVE_LOAD_FILE = BASE_DIR / "data" / "cognitive_load_summary.csv"
FLOW_SESSIONS_FILE = BASE_DIR / "data" / "flow_sessions.csv"
CONTEXT_SWITCHING_FILE = BASE_DIR / "data" / "context_switching_summary.csv"

def _normalize_dev_filter(developer_id: Optional[str]) -> Optional[str]:
    if not developer_id or developer_id.strip().lower() == "all":
        return None
    return developer_id.strip()

# ============================================
# 3. HOME & HEALTH ENDPOINTS
# ============================================

@app.get("/")
def home():
    return {
        "project": "CogniStream",
        "message": "Developer Analytics API is running!",
        "storage": "ClickHouse (cognitstream.activity_events)"
    }

@app.get("/health")
def health():
    try:
        client = get_clickhouse_client()
        version = client.command("SELECT version()")
        client.close()
        return {"status": "healthy", "clickhouse": "connected", "version": version}
    except Exception as exc:
        return {"status": "degraded", "clickhouse": "disconnected", "error": str(exc)}

# ============================================
# 4. DEVELOPER ANALYTICS (CLICKHOUSE)
# ============================================

@app.get("/developers")
def get_developers():
    try:
        client = get_clickhouse_client()
        result = client.query(
            """
            SELECT
                developer_id,
                count() AS total_events
            FROM cognitstream.activity_events
            GROUP BY developer_id
            ORDER BY developer_id
            """
        )
        client.close()
        return [
            {"developer_id": row[0], "total_events": int(row[1])}
            for row in result.result_rows
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ClickHouse query failed: {exc}")

# ============================================
# 5. EVENT SUMMARY (CLICKHOUSE)
# ============================================

@app.get("/event-summary")
def event_summary(developer_id: Optional[str] = Query(default=None)):
    dev_id = _normalize_dev_filter(developer_id)
    try:
        client = get_clickhouse_client()
        if dev_id:
            result = client.query(
                """
                SELECT event_type, count() AS total_events
                FROM cognitstream.activity_events
                WHERE developer_id = {dev_id:String}
                GROUP BY event_type
                ORDER BY event_type
                """,
                parameters={"dev_id": dev_id},
            )
        else:
            result = client.query(
                """
                SELECT event_type, count() AS total_events
                FROM cognitstream.activity_events
                GROUP BY event_type
                ORDER BY event_type
                """
            )
        client.close()
        return [
            {"event_type": row[0], "total_events": int(row[1])}
            for row in result.result_rows
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ClickHouse query failed: {exc}")

# ============================================
# 6. RECENT ACTIVITY (CLICKHOUSE)
# ============================================

@app.get("/activity")
def get_activity(developer_id: Optional[str] = Query(default=None)):
    dev_id = _normalize_dev_filter(developer_id)
    try:
        client = get_clickhouse_client()
        if dev_id:
            total_events = int(
                client.command(
                    "SELECT count() FROM cognitstream.activity_events WHERE developer_id = {dev_id:String}",
                    parameters={"dev_id": dev_id},
                )
            )
            result = client.query(
                """
                SELECT
                    developer_id,
                    event_type,
                    toString(timestamp) AS timestamp,
                    source
                FROM cognitstream.activity_events
                WHERE developer_id = {dev_id:String}
                ORDER BY timestamp ASC
                LIMIT 20
                """,
                parameters={"dev_id": dev_id},
            )
        else:
            total_events = int(client.command("SELECT count() FROM cognitstream.activity_events"))
            result = client.query(
                """
                SELECT
                    developer_id,
                    event_type,
                    toString(timestamp) AS timestamp,
                    source
                FROM cognitstream.activity_events
                ORDER BY timestamp ASC
                LIMIT 20
                """
            )
        client.close()
        events = [
            {
                "developer_id": row[0],
                "event_type": row[1],
                "timestamp": row[2],
                "source": row[3],
            }
            for row in result.result_rows
        ]
        return {
            "total_events": total_events,
            "events": events,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ClickHouse query failed: {exc}")

# ============================================
# 7. COGNITIVE LOAD ANALYSIS
# ============================================

@app.get("/cognitive-load")
def get_cognitive_load(developer_id: Optional[str] = Query(default=None)):
    if not COGNITIVE_LOAD_FILE.exists():
        return {"error": "Cognitive load report not found"}

    df = pl.read_csv(COGNITIVE_LOAD_FILE)
    dev_id = _normalize_dev_filter(developer_id)
    if dev_id and "developer_id" in df.columns:
        df = df.filter(pl.col("developer_id") == dev_id)

    return {
        "total_developers": df.height,
        "cognitive_load": df.to_dicts()
    }

# ============================================
# 8. FLOW-STATE ANALYSIS
# ============================================

@app.get("/flow-sessions")
def get_flow_sessions(developer_id: Optional[str] = Query(default=None)):
    if not FLOW_SESSIONS_FILE.exists():
        return {"error": "Flow sessions report not found"}

    df = pl.read_csv(FLOW_SESSIONS_FILE)
    dev_id = _normalize_dev_filter(developer_id)
    if dev_id and "developer_id" in df.columns:
        df = df.filter(pl.col("developer_id") == dev_id)

    return {
        "total_sessions": df.height,
        "flow_sessions": df.to_dicts()
    }

# ============================================
# 9. CONTEXT SWITCHING ANALYSIS
# ============================================

@app.get("/context-switching")
def get_context_switching(developer_id: Optional[str] = Query(default=None)):
    if not CONTEXT_SWITCHING_FILE.exists():
        return []

    df = pl.read_csv(CONTEXT_SWITCHING_FILE)
    dev_id = _normalize_dev_filter(developer_id)
    if dev_id and "developer_id" in df.columns:
        df = df.filter(pl.col("developer_id") == dev_id)

    return df.to_dicts()