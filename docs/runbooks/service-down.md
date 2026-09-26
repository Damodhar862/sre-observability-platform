# Runbook: OrdersServiceDown

**Severity:** page  **Impact:** Prometheus cannot reach the service - it may be completely down.

1. `docker compose ps` / `kubectl -n orders get pods` - are containers running? Restarting?
2. `kubectl -n orders describe pod <pod>` - look for OOMKilled, CrashLoopBackOff, failed probes.
3. Logs: `docker compose logs app` / `kubectl -n orders logs <pod> --previous`
4. Mitigate: `docker compose up -d app` or roll back the deployment.
5. Note: while this alert fires, Alertmanager inhibits the other page alerts to avoid alert noise.
