
import os
import clickhouse_connect


# ClickHouse Configuration
CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "admin"

# Read password from environment variable
CLICKHOUSE_PASSWORD = os.getenv(
    "CLICKHOUSE_PASSWORD",
    ""
)


def get_clickhouse_client():
    """
    Create and return a ClickHouse database connection.
    """

    client = clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        connect_timeout=10
    )

    return client


def test_connection():
    """
    Test ClickHouse connection and display server details.
    """

    try:
        client = get_clickhouse_client()

        result = client.query(
            "SELECT version(), currentUser()"
        )

        version = result.result_rows[0][0]
        username = result.result_rows[0][1]

        print("================================")
        print("CogniStream ClickHouse Connection")
        print("================================")
        print("Connection Status: SUCCESS")
        print("ClickHouse Version:", version)
        print("Connected User:", username)
        print("================================")

        client.close()

    except Exception as error:
        print("ClickHouse Connection Failed!")
        print("Error:", error)


if __name__ == "__main__":
    test_connection()
