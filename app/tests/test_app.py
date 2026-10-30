"""Unit tests for the SRE demo app."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app  # noqa: E402

client = app.test_client()


def test_index():
    res = client.get("/")
    assert res.status_code == 200
    assert res.get_json()["service"] == "sre-demo-app"


def test_health_and_readiness():
    assert client.get("/healthz").status_code == 200
    assert client.get("/readyz").status_code == 200


def test_create_order():
    res = client.post("/api/orders", json={"product": "latte"})
    assert res.status_code == 201
    assert res.get_json()["product"] == "latte"
    assert client.get("/api/orders").get_json()["orders"]["latte"] >= 1


def test_create_order_rejects_unknown_product():
    assert client.post("/api/orders", json={"product": "tea"}).status_code == 400


def test_error_endpoint_returns_500():
    assert client.get("/api/error").status_code == 500


def test_metrics_are_exposed():
    client.get("/")
    client.get("/api/error")
    body = client.get("/metrics").get_data(as_text=True)
    assert "demo_http_requests_total" in body
    assert "demo_http_request_duration_seconds_bucket" in body
    assert "demo_orders_created_total" in body
    assert 'endpoint="/api/error",method="GET",status="500"' in body


def test_probes_are_not_counted_as_traffic():
    client.get("/healthz")
    body = client.get("/metrics").get_data(as_text=True)
    assert 'endpoint="/healthz"' not in body
