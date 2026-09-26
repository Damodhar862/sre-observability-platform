# Runbook: OrdersErrorBudgetFastBurn / SlowBurn

**Severity:** page (fast) / ticket (slow)
**Impact:** users are getting 5xx errors from `/orders`.

## 1. Confirm (2 min)
- Grafana > SRE > *Orders Service - SLO Overview*: is "Error ratio" above the red line?
- Prometheus: `sum by (status) (rate(http_requests_total{path="/orders"}[5m]))`

## 2. Find what changed (5 min)
- Recent deploy? `kubectl -n orders rollout history deployment/orders-service`
- Chaos experiment left on? `./scripts/chaos.sh status`
- App logs: `docker compose logs app --tail 100` or `kubectl -n orders logs deploy/orders-service --tail 100`

## 3. Mitigate (restore service first, debug later)
- Bad deploy -> `kubectl -n orders rollout undo deployment/orders-service`
- Chaos left on -> `./scripts/chaos.sh reset`
- Overloaded -> `kubectl -n orders scale deployment/orders-service --replicas=4`

## 4. Verify
Error ratio back under 0.5% for 10+ minutes and the alert resolves.

## 5. Follow up
Write a postmortem using `docs/postmortem-template.md` if the page lasted > 15 minutes.
