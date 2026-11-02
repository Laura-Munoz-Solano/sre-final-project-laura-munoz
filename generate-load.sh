#!/bin/bash

# Sends traffic to the app so the dashboard has data and the alerts can fire.
#
# Usage: ./generate-load.sh [normal|errors|slow] [seconds]
#   normal -> normal traffic (default)
#   errors -> about 30% of the loops also call /api/error (HighErrorRate alert)
#   slow   -> about 30% of the loops also call /api/slow (HighLatency alert)
#
# The app must be open on localhost:8080 (./port-forward.sh)

MODE="${1:-normal}"
DURATION="${2:-300}"
URL="http://localhost:8080"
PRODUCTS=(espresso latte cappuccino americano)
END=$((SECONDS + DURATION))

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Sending '$MODE' traffic to $URL for $DURATION seconds (Ctrl+C to stop)"

while [ $SECONDS -lt $END ]; do
  product="${PRODUCTS[RANDOM % ${#PRODUCTS[@]}]}"
  curl -s -o /dev/null -X POST "$URL/api/orders" -H 'Content-Type: application/json' -d "{\"product\":\"$product\"}"
  curl -s -o /dev/null "$URL/api/orders"
  curl -s -o /dev/null "$URL/"

  if [ $((RANDOM % 10)) -lt 3 ]; then
    if [ "$MODE" == "errors" ]; then
      curl -s -o /dev/null "$URL/api/error"
    elif [ "$MODE" == "slow" ]; then
      curl -s -o /dev/null "$URL/api/slow" &
    fi
  fi

  sleep 0.1
done

wait
log "Done."
