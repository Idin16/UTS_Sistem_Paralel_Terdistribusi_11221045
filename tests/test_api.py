from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestHealthCheck:
    def test_root_endpoint(self):
        """Pastikan endpoint root mengembalikan info sistem"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        # Sesuaikan nama sesuai main.py
        assert data["service"] == "UTS Aggregator System"
