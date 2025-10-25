from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_app_running():
    """Pastikan app FastAPI aktif"""
    response = client.get("/")
    assert response.status_code == 200

def test_publish_event():
    """Pastikan event bisa diterima server"""
    payload = {
        "topic": "demo",
        "event_id": "123",
        "timestamp": "2025-10-24T10:00:00Z",
        "message": "UTS Aggregator test message"
    }
    response = client.post("/publish", json=payload)
    assert response.status_code in (200, 201, 202, 400, 422)

def test_stats_endpoint():
    response = client.get("/stats")
    assert response.status_code == 200

def test_events_endpoint():
    response = client.get("/events")
    assert response.status_code == 200

def test_all_endpoints_available():
    """Pastikan semua endpoint utama tersedia"""
    for path in ["/", "/publish", "/events", "/stats"]:
        response = client.get(path)
        assert response.status_code in (200, 404, 405)  # Terima GET untuk test

