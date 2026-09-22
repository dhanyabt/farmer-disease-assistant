from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check_returns_success():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_with_valid_request_returns_ok():
    response = client.post(
        "/analyze",
        json={
            "crop": "Tomato",
            "disease": "Early Blight",
            "confidence": 0.87,
            "symptoms": "brown spots on older leaves",
        },
    )

    assert response.status_code == 200


def test_analyze_with_confidence_below_zero_returns_unprocessable_entity():
    response = client.post(
        "/analyze",
        json={
            "crop": "Tomato",
            "disease": "Early Blight",
            "confidence": -0.1,
            "symptoms": "brown spots on older leaves",
        },
    )

    assert response.status_code == 422


def test_analyze_with_confidence_above_one_returns_unprocessable_entity():
    response = client.post(
        "/analyze",
        json={
            "crop": "Tomato",
            "disease": "Early Blight",
            "confidence": 1.1,
            "symptoms": "brown spots on older leaves",
        },
    )

    assert response.status_code == 422


def test_analyze_with_missing_required_fields_returns_unprocessable_entity():
    response = client.post(
        "/analyze",
        json={
            "crop": "Tomato",
        },
    )

    assert response.status_code == 422