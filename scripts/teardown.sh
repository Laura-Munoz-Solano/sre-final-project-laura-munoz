#!/usr/bin/env bash
# Removes everything installed by setup.sh (the Minikube cluster is kept).
set -uo pipefail
helm uninstall sre-demo-app -n demo
helm uninstall monitoring -n monitoring
kubectl delete namespace demo monitoring
