import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_toxic_input_is_flagged(client):
    response = client.post("/check", json={"text": "I hate you"})
    assert response.status_code == 200
    assert response.json()["safe"] == False

def test_pii_input_is_flagged(client):
    response = client.post("/check", json={"text": "My phone number is 212-555-5555"})
    assert response.status_code == 200
    assert response.json()["safe"] == False