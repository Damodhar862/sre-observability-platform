# Runbook: OrdersHighLatencyP95

**Severity:** page  **Impact:** `/orders` p95 is above 300ms - users feel the app is slow.

1. **Confirm:** Grafana "Latency percentiles" panel. Is only p99 high (a few slow requests) or p50 too (everything slow)?
2. **Check saturation:** "Requests in flight" rising? -> service is overloaded.
   `kubectl -n orders top pods` (needs metrics-server).
3. **Check injected latency:** `./scripts/chaos.sh status`
4. **Mitigate:** reset chaos, scale out, or roll back the last deploy.
5. **Verify:** p95 < 300ms for 10 minutes.
