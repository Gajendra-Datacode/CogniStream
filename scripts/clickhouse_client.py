import os
from pathlib import Path
import clickhouse_connect

# Load .env from project root if present
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip() and not line.strip().startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

# ClickHouse Configuration
CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "admin"
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "YourStrongPassword123")


def get_clickhouse_client():
    """Create and return a ClickHouse database connection."""
    client = clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database="cognitstream",
        connect_timeout=10,
    )
    return client


def test_connection():
    """Test ClickHouse connection and display server details."""
    try:
        client = get_clickhouse_client()
        result = client.query("SELECT version(), currentUser()")
        version = result.result_rows[0][0]
        username = result.result_rows[0][1]

        print("====================================")
        print("CogniStream ClickHouse Connection")
        print("====================================")
        print("Connection Status: SUCCESS")
        print("ClickHouse Version:", version)
        print("Connected User:", username)
        print("====================================")
        client.close()
    except Exception as error:
        print("ClickHouse Connection Failed!")
        print("Error:", error)


if __name__ == "__main__":
    test_connection()
