#!/usr/bin/env bash
# Sends traffic to the app so the dashboards have data and alerts can fire.
#
# Usage: ./scripts/generate-load.sh [normal|errors|slow] [duration_seconds]
#   normal  healthy traffic (default)
#   errors  ~30% of requests hit /api/error  -> fires DemoAppHighErrorRate
#   slow    ~30% of requests hit /api/slow   -> fires DemoAppHighLatency
set -uo pipefail

MODE="${1:-normal}"
DURATION="${2:-300}"
URL="${APP_URL:-http://localhost:8080}"
PRODUCTS=(espresso latte cappuccino americano)
END=$((SECONDS + DURATION))

echo "Sending '${MODE}' traffic to ${URL} for ${DURATION}s (Ctrl+C to stop)"
while (( SECONDS < END )); do
  product="${PRODUCTS[RANDOM % ${#PRODUCTS[@]}]}"
  curl -s -o /dev/null -X POST "${URL}/api/orders" \
    -H 'Content-Type: application/json' -d "{\"product\":\"${product}\"}"
  curl -s -o /dev/null "${URL}/api/orders"
  curl -s -o /dev/null "${URL}/"
  if (( RANDOM % 10 < 3 )); then
    case "${MODE}" in
      errors) curl -s -o /dev/null "${URL}/api/error" ;;
      slow)   curl -s -o /dev/null "${URL}/api/slow" & ;;
    esac
  fi
  sleep 0.1
done
wait
echo "Done."
