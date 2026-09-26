# Service Level Objectives - orders-service

| SLI | How it's measured | SLO (30-day) | Error budget |
|---|---|---|---|
| Availability | non-5xx `/orders` responses / all `/orders` responses | 99.5% | 0.5% (~3h 36m of full outage) |
| Latency | `/orders` requests served in < 300ms | 95% | 5% of requests may be slower |

## Error budget policy
- **Budget > 50% left:** ship features normally.
- **Budget 0-50% left:** prioritise reliability fixes in the next sprint.
- **Budget exhausted:** freeze non-critical releases until the 30-day window recovers.

## Alerting strategy
Multi-window, multi-burn-rate alerts (Google SRE Workbook):

| Alert | Condition | Meaning | Action |
|---|---|---|---|
| FastBurn | 1h AND 5m error ratio > 14.4 x budget | 2% of monthly budget gone in 1 hour | Page |
| SlowBurn | 6h AND 30m error ratio > 6 x budget | 5% of monthly budget gone in 6 hours | Ticket |

The short window makes the alert **resolve quickly** once the problem is fixed; the long window stops it **flapping** on brief blips.
