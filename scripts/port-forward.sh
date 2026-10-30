#!/usr/bin/env bash
# Exposes the app and the monitoring UIs on localhost. Stop with Ctrl+C.
set -euo pipefail
trap 'kill $(jobs -p) 2>/dev/null' EXIT

kubectl -n demo       port-forward svc/sre-demo-app 8080:8080 &
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 &
kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-alertmanager 9093:9093 &
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80 &
wait
