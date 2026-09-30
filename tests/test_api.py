import os

os.environ["DEMO_MODE"] = "true"

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "LegalEase" in response.json()["message"]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate():
    payload = {
        "document_type": "Freelance Work Contract",
        "parties": "Jane Doe (Service Provider), TechNova Inc. (Client)",
        "terms": "Payment within 30 days; Confidentiality must be maintained",
        "dates": "30 September 2026",
    }
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["document"]
    assert "Freelance Work Contract" in body["document"]
