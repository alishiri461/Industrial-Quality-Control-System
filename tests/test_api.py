from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def test_health_liveness() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_inspection_fails_closed_without_inference() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/inspections",
            json={"product_type": "refrigerator", "camera_id": "line-01-camera-01"},
        )
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "INFERENCE_NOT_CONFIGURED"


def test_model_registry_does_not_claim_production_validation() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/models")
    assert response.status_code == 200
    assert response.json()["production_validated"] is False
