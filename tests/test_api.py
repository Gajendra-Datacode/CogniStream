from fastapi.testclient import TestClient
from scripts.api import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_developers():
    response = client.get("/developers")
    assert response.status_code == 200


def test_event_summary():
    response = client.get("/event-summary")
    assert response.status_code == 200


def test_activity():
    response = client.get("/activity")
    assert response.status_code == 200


def test_cognitive_load():
    response = client.get("/cognitive-load")
    assert response.status_code == 200


def test_flow_sessions():
    response = client.get("/flow-sessions")
    assert response.status_code == 200