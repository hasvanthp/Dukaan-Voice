from fastapi.testclient import TestClient


def test_low_confidence_triggers_clarification(client: TestClient, headers: dict[str, str]) -> None:
    payload = {"text": "hello", "confirmed": False}
    response = client.post("/api/v1/conversation/voice-command", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["requires_confirmation"] is False
    assert "clear" in body["message"].lower()


def test_correction_uses_latest_quantity(client: TestClient, headers: dict[str, str]) -> None:
    payload = {"text": "2 kilo sugar add karo... nahi, 3 kilo", "confirmed": False}
    response = client.post("/api/v1/conversation/voice-command", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "add_inventory"
    assert body["requires_confirmation"] is True
    assert body["preview_action"]["entities"]["quantity"] == 3.0
