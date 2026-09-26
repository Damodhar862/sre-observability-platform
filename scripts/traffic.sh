#!/usr/bin/env bash
# Lightweight background traffic so dashboards always have data.
#   ./scripts/traffic.sh      (Ctrl+C to stop)
set -uo pipefail
URL="${APP_URL:-http://localhost:8000}"
echo "Sending traffic to $URL ... Ctrl+C to stop"
while true; do
  curl -s -o /dev/null -X POST "$URL/orders" -H 'Content-Type: application/json' -d '{"item":"widget","quantity":1}'
  curl -s -o /dev/null "$URL/orders"
  sleep 0.2
done
