"""SRE Demo App - a small "coffee shop" orders API instrumented with Prometheus.

The business logic is intentionally simple: the goal of this service is to
expose meaningful metrics (traffic, errors, latency, saturation) so that the
monitoring stack around it (Prometheus, Grafana, Alertmanager) can be exercised.

Endpoints
---------
GET  /             Service information
GET  /api/orders   Summary of the orders created so far
POST /api/orders   Create an order (can fail randomly, see ERROR_RATE)
GET  /api/slow     Simulates a slow dependency (used to trigger latency alerts)
GET  /api/error    Always returns HTTP 500 (used to trigger error-rate alerts)
GET  /healthz      Liveness probe
GET  /readyz       Readiness probe
GET  /metrics      Prometheus metrics
"""
import os
import random
import time

from flask import Flask, Response, g, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
# Probability (0.0 - 1.0) that POST /api/orders fails. Lets us inject failures
# without redeploying code: `helm upgrade --set errorRate=0.5`.
ERROR_RATE = float(os.getenv("ERROR_RATE", "0.0"))
PRODUCTS = ["espresso", "latte", "cappuccino", "americano"]

app = Flask(__name__)

# --------------------------------------------------------------------------
# Metrics. They follow the "four golden signals": traffic, errors, latency
# and saturation. All of them share the `demo_` prefix.
# --------------------------------------------------------------------------
APP_INFO = Info("demo_app", "Static information about the application")
APP_INFO.info({"version": APP_VERSION})

REQUESTS = Counter(
    "demo_http_requests_total",
    "Total HTTP requests handled",
    ["method", "endpoint", "status"],
)
LATENCY = Histogram(
    "demo_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
IN_PROGRESS = Gauge(
    "demo_http_requests_in_progress",
    "HTTP requests currently being processed",
)
ORDERS = Counter(
    "demo_orders_created_total",
    "Orders successfully created, by product",
    ["product"],
)

# Paths that should not be counted as user traffic.
EXCLUDED_PATHS = {"/metrics", "/healthz", "/readyz"}


def _endpoint_label():
    """Return the route template (not the raw path) to keep cardinality low."""
    return request.url_rule.rule if request.url_rule else "unmatched"


@app.before_request
def _start_timer():
    if request.path in EXCLUDED_PATHS:
        return
    g.start_time = time.perf_counter()
    IN_PROGRESS.inc()


@app.after_request
def _record_metrics(response):
    start = g.pop("start_time", None)
    if start is None:
        return response
    endpoint = _endpoint_label()
    LATENCY.labels(request.method, endpoint).observe(time.perf_counter() - start)
    REQUESTS.labels(request.method, endpoint, str(response.status_code)).inc()
    IN_PROGRESS.dec()
    return response


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.get("/")
def index():
    return jsonify(service="sre-demo-app", version=APP_VERSION, status="ok")


@app.get("/api/orders")
def list_orders():
    totals = {p: int(ORDERS.labels(p)._value.get()) for p in PRODUCTS}
    return jsonify(orders=totals, total=sum(totals.values()))


@app.post("/api/orders")
def create_order():
    payload = request.get_json(silent=True) or {}
    product = payload.get("product") or random.choice(PRODUCTS)
    if product not in PRODUCTS:
        return jsonify(error=f"unknown product '{product}'", valid=PRODUCTS), 400

    # Simulated processing time and injected failures.
    time.sleep(random.uniform(0.005, 0.08))
    if random.random() < ERROR_RATE:
        return jsonify(error="order processing failed"), 500

    ORDERS.labels(product).inc()
    return jsonify(status="created", product=product), 201


@app.get("/api/slow")
def slow():
    delay = random.uniform(0.8, 2.5)
    time.sleep(delay)
    return jsonify(status="ok", delay_seconds=round(delay, 2))


@app.get("/api/error")
def error():
    return jsonify(error="simulated failure"), 500


@app.get("/healthz")
def healthz():
    return jsonify(status="alive")


@app.get("/readyz")
def readyz():
    return jsonify(status="ready")


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
