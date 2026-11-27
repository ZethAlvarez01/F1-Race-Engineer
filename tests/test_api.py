from fastapi.testclient import TestClient

from backend.api import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_race_metrics_rejects_invalid_session_key():
    with TestClient(app) as client:
        response = client.get("/api/v1/race-metrics?session_key=abc")

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"] == ["query", "session_key"] for error in errors)


def test_race_metrics_returns_two_drivers(monkeypatch):
    metrics = [
        {
            "session_key": 9165,
            "driver_number": 4,
            "valid_laps": 57,
            "avg_lap_duration": 99.794,
            "fastest_lap": 98.046,
        },
        {
            "session_key": 9165,
            "driver_number": 55,
            "valid_laps": 57,
            "avg_lap_duration": 99.678,
            "fastest_lap": 97.666,
        },
    ]
    received_session_keys = []

    def fake_get_gold_metrics(session_key):
        received_session_keys.append(session_key)
        return metrics

    monkeypatch.setattr("backend.api.get_gold_metrics", fake_get_gold_metrics)

    with TestClient(app) as client:
        response = client.get("/api/v1/race-metrics?session_key=9165")

    assert response.status_code == 200
    assert response.json() == metrics
    assert received_session_keys == [9165]
