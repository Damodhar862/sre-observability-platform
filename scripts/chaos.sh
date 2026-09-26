#!/usr/bin/env bash
# Fault injection helper.
#   ./scripts/chaos.sh errors 0.3     -> 30% of /orders requests return 500
#   ./scripts/chaos.sh latency 600    -> add 600ms to every /orders request
#   ./scripts/chaos.sh reset          -> back to normal
#   ./scripts/chaos.sh status
set -euo pipefail
URL="${APP_URL:-http://localhost:8000}"

case "${1:-status}" in
  errors)  body="{\"error_rate\": ${2:?rate 0-1}, \"latency_ms\": 0}" ;;
  latency) body="{\"error_rate\": 0, \"latency_ms\": ${2:?milliseconds}}" ;;
  reset)   body='{"error_rate": 0, "latency_ms": 0}' ;;
  status)  curl -s "$URL/chaos"; echo; exit 0 ;;
  *) echo "usage: $0 {errors <rate>|latency <ms>|reset|status}"; exit 1 ;;
esac

curl -s -X POST "$URL/chaos" -H 'Content-Type: application/json' -d "$body"; echo
