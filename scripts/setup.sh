#!/usr/bin/env bash
# Deploys the whole project on a local Minikube cluster:
#   1. starts Minikube
#   2. installs Prometheus + Grafana + Alertmanager (kube-prometheus-stack)
#   3. builds the app image inside Minikube
#   4. installs the app with its Helm chart
#
# Optional: export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/... to
# enable Slack notifications.
set -euo pipefail
cd "$(dirname "$0")/.."

IMAGE_TAG="1.0.0"

echo "==> Starting Minikube"
minikube status >/dev/null 2>&1 || minikube start --cpus=4 --memory=6g

echo "==> Installing kube-prometheus-stack"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null
helm repo update >/dev/null

EXTRA_ARGS=()
if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
  echo "    Slack notifications: enabled"
  EXTRA_ARGS+=(-f monitoring/alertmanager-slack-values.yaml
    --set-string "alertmanager.config.global.slack_api_url=${SLACK_WEBHOOK_URL}")
else
  echo "    Slack notifications: disabled (SLACK_WEBHOOK_URL is not set)"
fi

helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f monitoring/kube-prometheus-stack-values.yaml \
  ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"} \
  --wait --timeout 10m

echo "==> Building the application image inside Minikube"
minikube image build -t "sre-demo-app:${IMAGE_TAG}" app/

echo "==> Installing sre-demo-app"
helm upgrade --install sre-demo-app charts/sre-demo-app \
  --namespace demo --create-namespace \
  --set image.tag="${IMAGE_TAG}" \
  --wait --timeout 3m

cat <<MSG

Done. Run ./scripts/port-forward.sh and open:
  App           http://localhost:8080
  Prometheus    http://localhost:9090
  Alertmanager  http://localhost:9093
  Grafana       http://localhost:3000   (admin / sre-academy)
MSG
