# Postmortem: Elevated 5xx errors on orders-service (chaos game day)

*Planned fault-injection experiment, written up as practice for real incidents. Blameless format.*

| Field | Value |
|---|---|
| Date | 26 September 2026 |
| Duration of user impact | ~43 minutes (~19:00 to ~19:43) |
| Severity | SEV-2 (partial outage, ~50% of /orders requests failing) |
| Lowest 1h availability | ~85.5% (SLO: 99.5%) |
| Peak 1h burn rate | ~29x (fast-burn page threshold: 14.4x) |

## Summary
A fault-injection experiment set a 50% error rate on `/orders`. Availability dropped well below the 99.5% SLO,
both error-budget burn-rate alerts fired, the runbook was followed to find and remove the cause,
and the fast-burn alert resolved within minutes of mitigation.

## Timeline (local time)
| Time | Event |
|---|---|
| ~18:45 | Baseline load test with k6: 9,902 requests, 0% errors, p95 114ms |
| ~19:00 | `chaos.sh errors 0.5` applied - 50% of /orders requests return 500 |
| ~19:00 | Error ratio (5m) jumps from 0% to ~50% on the Grafana dashboard |
| 19:36 | `OrdersErrorBudgetFastBurn` (page) firing - Prometheus "Active Since" 14:06:45 UTC; it re-fired after the traffic gap |
| ~19:27 - 19:36 | Traffic generator stopped; dashboards showed a gap in data |
| ~19:42 | Runbook step 2: `chaos.sh status` identified error_rate=0.5 as the cause |
| ~19:43 | Mitigation: `chaos.sh reset` |
| ~19:47 | `OrdersErrorBudgetFastBurn` resolved; SlowBurn still firing (longer windows) |

![Grafana during the incident](images/grafana-incident.png)

![Alerts firing](images/alert-firing.png)

![Fast-burn alert resolved after mitigation](images/alert-resolved.png)

## Root cause
The chaos endpoint was configured to fail 50% of requests. In a real system the equivalent would be
a bad deploy or a failing dependency.

## What went well
- The dashboard made the problem obvious within 1-2 minutes (availability, burn rate and error ratio all turned red).
- Only the relevant alerts fired. Latency and service-down alerts stayed quiet because the service was up and fast.
- The runbook led straight to the cause and the fix.
- Thanks to the short (5m) window, the fast-burn alert cleared within minutes of the fix,
  even though the 1h burn rate stayed high.

## What went wrong / what I learned
- Alert detection took longer than expected: roughly 10,000 successful load-test requests earlier in the
  hour diluted the 1h error ratio. This is by design (it prevents paging on short blips) but it is worth knowing.
- When the traffic generator stopped, the SLI showed "no data" instead of alerting. A lack of traffic can hide an outage.
- The first version of the recording rules returned "no data" when there were zero errors, so the availability panel
  was blank. Fixed by adding `or vector(0)` to the error-count part of each ratio.

## Action items
| Action | Status |
|---|---|
| Add `or vector(0)` so SLIs report 0 errors instead of no data | Done |
| Add an alert for missing traffic (`absent()` / zero request rate) | To do |
| Disable the `/chaos` endpoint outside test environments (`CHAOS_ENABLED=false`) | To do |
