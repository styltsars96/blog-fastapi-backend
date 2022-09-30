"""
Basic health check test
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """test_health_check
    Test that API server is up
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}
