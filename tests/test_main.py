from fastapi.testclient import TestClient

from app.main import app, chaos

client = TestClient(app)


def reset_chaos():
    client.post("/chaos", json={"error_rate": 0, "latency_ms": 0})


def test_health_and_ready():
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200


def test_create_and_list_orders():
    reset_chaos()
    r = client.post("/orders", json={"item": "keyboard", "quantity": 2})
    assert r.status_code == 201
    assert r.json()["item"] == "keyboard"
    assert client.get("/orders").json()["count"] >= 1


def test_validation_rejects_bad_order():
    r = client.post("/orders", json={"item": "", "quantity": 0})
    assert r.status_code == 422


def test_chaos_forces_errors_then_recovers():
    client.post("/chaos", json={"error_rate": 1.0, "latency_ms": 0})
    assert client.get("/orders").status_code == 500
    reset_chaos()
    assert chaos.error_rate == 0
    assert client.get("/orders").status_code == 200


def test_metrics_exposed_with_status_labels():
    reset_chaos()
    client.get("/orders")
    body = client.get("/metrics").text
    assert "http_requests_total" in body
    assert 'path="/orders"' in body
    assert "http_request_duration_seconds_bucket" in body
