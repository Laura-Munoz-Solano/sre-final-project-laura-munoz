import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app  # noqa: E402

client = app.test_client()


def test_home():
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json()['service'] == 'sre-demo-app'


def test_health_checks():
    assert client.get('/healthz').status_code == 200
    assert client.get('/readyz').status_code == 200


def test_create_order():
    response = client.post('/api/orders', json={'product': 'latte'})
    assert response.status_code == 201
    assert client.get('/api/orders').get_json()['orders']['latte'] >= 1


def test_unknown_product():
    response = client.post('/api/orders', json={'product': 'tea'})
    assert response.status_code == 400


def test_error_endpoint():
    assert client.get('/api/error').status_code == 500


def test_metrics_endpoint():
    client.get('/')
    client.get('/api/error')
    body = client.get('/metrics').get_data(as_text=True)
    assert 'http_requests_total' in body
    assert 'http_request_duration_seconds_bucket' in body
    assert 'endpoint="/api/error",method="GET",status="500"' in body


def test_health_checks_are_not_counted():
    client.get('/healthz')
    body = client.get('/metrics').get_data(as_text=True)
    assert 'endpoint="/healthz"' not in body
