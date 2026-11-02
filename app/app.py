from flask import Flask, Response, jsonify, request, g
import os
import random
import time

# Prometheus client imports
from prometheus_client import generate_latest, Counter, Histogram, Gauge, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Probability (0 to 1) that POST /api/orders fails. I use it to test the alerts.
ERROR_RATE = float(os.getenv("ERROR_RATE", "0"))

PRODUCTS = ["espresso", "latte", "cappuccino", "americano"]
orders = {product: 0 for product in PRODUCTS}

# --- Prometheus Metrics Setup ---
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests',
                        ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency',
                            ['method', 'endpoint'])
REQUESTS_IN_PROGRESS = Gauge('http_requests_in_progress', 'HTTP Requests being processed right now')
ORDERS_CREATED = Counter('orders_created_total', 'Total orders created', ['product'])

# The health checks and /metrics are not counted as user traffic
SKIP_PATHS = ['/metrics', '/healthz', '/readyz']


@app.before_request
def start_timer():
    if request.path in SKIP_PATHS:
        return
    g.start_time = time.time()  # Start timer for latency
    REQUESTS_IN_PROGRESS.inc()


@app.after_request
def record_metrics(response):
    if request.path in SKIP_PATHS or 'start_time' not in g:
        return response

    # Use the route (ex: /api/orders) instead of the full url
    endpoint = request.url_rule.rule if request.url_rule else 'unknown'

    latency = time.time() - g.start_time  # Calculate latency
    REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(latency)
    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint,
                         status=response.status_code).inc()
    REQUESTS_IN_PROGRESS.dec()
    return response


@app.route('/')
def hello_world():
    return jsonify(service="sre-demo-app", status="ok")


@app.get('/api/orders')
def get_orders():
    return jsonify(orders=orders, total=sum(orders.values()))


@app.post('/api/orders')
def create_order():
    data = request.get_json(silent=True) or {}
    product = data.get('product') or random.choice(PRODUCTS)
    if product not in PRODUCTS:
        return jsonify(error=f"unknown product {product}"), 400

    time.sleep(random.uniform(0.005, 0.08))  # Simulate some work

    # Fail on purpose depending on ERROR_RATE
    if random.random() < ERROR_RATE:
        return jsonify(error="order processing failed"), 500

    orders[product] += 1
    ORDERS_CREATED.labels(product=product).inc()
    return jsonify(status="created", product=product), 201


# Slow endpoint, used to test the latency alert
@app.get('/api/slow')
def slow():
    delay = random.uniform(0.8, 2.5)
    time.sleep(delay)
    return jsonify(status="ok", delay_seconds=round(delay, 2))


# Always fails, used to test the error rate alert
@app.get('/api/error')
def error():
    return jsonify(error="simulated failure"), 500


# Liveness and readiness probes for Kubernetes
@app.get('/healthz')
def healthz():
    return jsonify(status="alive")


@app.get('/readyz')
def readyz():
    return jsonify(status="ready")


# Prometheus metrics endpoint
@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
