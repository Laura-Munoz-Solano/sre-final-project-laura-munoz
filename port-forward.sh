#!/bin/bash

# Opens the app and the monitoring UIs on localhost.
# Leave it running in its own terminal and stop it with Ctrl+C.

trap 'kill $(jobs -p) 2>/dev/null' EXIT

kubectl -n sre-app port-forward svc/sre-demo-app-service 8080:5000 &
kubectl -n monitoring port-forward svc/prometheus-service 9090:9090 &
kubectl -n monitoring port-forward svc/alertmanager 9093:9093 &
kubectl -n monitoring port-forward svc/grafana-service 3000:3000 &

wait
