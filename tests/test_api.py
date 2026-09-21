from fastapi.testclient import TestClient

from apps.api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_latest_assessment_falls_back_to_seeded_events():
    response = client.get("/assessments/latest")
    assert response.status_code == 200
    body = response.json()
    assert body["library"] == "Angular Material"
    assert any(event["component"] == "MatFormField" for event in body["changeEvents"])
