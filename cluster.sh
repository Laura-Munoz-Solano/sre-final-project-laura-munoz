#!/bin/bash

# Exit on failure
set -e

# ----------------------
# Utility Functions
# ----------------------

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

safe_run() {
  "$@" || { log "Command failed: $*"; exit 1; }
}

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

ensure_tool() {
  local tool="$1"
  if command_exists "$tool"; then
    log "$tool is installed."
  else
    log "$tool is not installed."
    if command_exists brew; then
      log "Installing $tool via Homebrew..."
      brew install "$tool" || { log "Failed to install $tool"; exit 1; }
    else
      log "Homebrew is missing. Please install it from https://brew.sh/"
      exit 1
    fi
  fi
}

pause() {
  log "Waiting for $1 seconds..."
  sleep "$1"
}

# -------------------------------
# Toolchain Check
# -------------------------------
log "=== SRE Final Project Setup ==="
log "Checking toolchain dependencies..."
for tool in colima minikube kubectl docker helm; do
  ensure_tool "$tool"
done

# -------------------------------
# Startup Phase (Colima and Minikube)
# -------------------------------
if colima status >/dev/null 2>&1; then
  log "Colima is already running."
else
  log "Starting Colima with Docker runtime..."
  safe_run colima start --cpu 4 --memory 8
  pause 5
fi

if minikube status >/dev/null 2>&1; then
  log "Minikube is already running."
else
  log "Starting Minikube with Docker driver..."
  safe_run minikube start --driver=docker --cpus=4 --memory=6g
  pause 5
fi

# -------------------------------
# Cleanup of a previous install
# -------------------------------
log "Removing previous install of the project (if it exists)..."
helm uninstall sre-app >/dev/null 2>&1 || true
safe_run kubectl delete ns sre-app monitoring --ignore-not-found=true
pause 5

# -------------------------------
# Docker Image Build
# -------------------------------
log "Building the app image inside Minikube..."
safe_run minikube image build -t sre-demo-app:1.0.0 ./app
pause 2

# -------------------------------
# Helm Install
# -------------------------------
if [[ -z "$SLACK_WEBHOOK_URL" ]]; then
  log "SLACK_WEBHOOK_URL is not set. Alerts will NOT be sent to Slack."
else
  log "SLACK_WEBHOOK_URL is set. Alerts will be sent to Slack."
fi

log "Installing the Helm chart..."
safe_run helm install sre-app ./sre-app-chart \
  --set-string slackWebhookUrl="${SLACK_WEBHOOK_URL:-}" \
  --wait --timeout=5m

# -------------------------------
# Pod Verification
# -------------------------------
log "Waiting for pod readiness..."
kubectl wait --for=condition=Ready pods --all -n sre-app --timeout=300s || log "Some app pods are not Ready"
kubectl wait --for=condition=Ready pods --all -n monitoring --timeout=300s || log "Some monitoring pods are not Ready"

log "Current pod status:"
kubectl get pods -n sre-app
kubectl get pods -n monitoring

log "=== Setup Complete ==="
log "Run ./port-forward.sh and open:"
log "  App:          http://localhost:8080"
log "  Prometheus:   http://localhost:9090"
log "  Alertmanager: http://localhost:9093"
log "  Grafana:      http://localhost:3000 (admin / admin)"
