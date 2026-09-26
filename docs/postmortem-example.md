# Postmortem: Elevated 5xx errors on orders-service (game day)

*Planned chaos experiment - written as practice for real incidents.*

| Field | Value |
|---|---|
| Date | <fill in the day you run it> |
| Duration | ~14 minutes |
| Severity | SEV-2 (partial outage) |
| Error budget consumed | <read from Grafana> |

## Summary
A fault-injection experiment set a 30% error rate on `/orders`. The `OrdersErrorBudgetFastBurn` alert fired, the runbook was followed, and service was restored.

## Timeline
| Time | Event |
|---|---|
| T+0 | `./scripts/chaos.sh errors 0.3` applied |
| T+? | Alert went to *pending*, then *firing* in Alertmanager |
| T+? | Runbook step 2 identified chaos flag as the cause |
| T+? | `./scripts/chaos.sh reset` applied |
| T+? | Alert resolved |

## What I learned
- Time-to-detect was <X> minutes; the `for: 2m` clause adds delay but prevents flapping.
- <Your own observations - fill these in honestly after running it.>

## Action items
- Protect the `/chaos` endpoint in production (`CHAOS_ENABLED=false`).
