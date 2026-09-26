"""orders-service: a small API instrumented for SRE practice (SLIs, SLOs, fault injection)."""
import asyncio
import os
import random
import time
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

app = FastAPI(title="orders-service", version="1.0.0")

# Only known paths become metric labels -> keeps label cardinality bounded.
KNOWN_PATHS = {"/orders", "/health", "/ready", "/chaos"}
MAX_ORDERS = 1000  # cap in-memory store so the service can't leak memory

REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.025, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.5, 5.0),
)
IN_PROGRESS = Gauge("http_requests_in_progress", "Requests currently being served")
CHAOS_ERROR_RATE = Gauge("chaos_error_rate", "Configured fault-injection error rate (0-1)")
CHAOS_LATENCY = Gauge("chaos_extra_latency_ms", "Configured fault-injection extra latency (ms)")


class ChaosConfig(BaseModel):
    error_rate: float = Field(0.0, ge=0.0, le=1.0)
    latency_ms: int = Field(0, ge=0, le=10000)


class OrderIn(BaseModel):
    item: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0, le=1000)


chaos = ChaosConfig(
    error_rate=float(os.getenv("ERROR_RATE", "0")),
    latency_ms=int(os.getenv("EXTRA_LATENCY_MS", "0")),
)
CHAOS_ENABLED = os.getenv("CHAOS_ENABLED", "true").lower() == "true"
orders: dict = {}


def publish_chaos_metrics() -> None:
    CHAOS_ERROR_RATE.set(chaos.error_rate)
    CHAOS_LATENCY.set(chaos.latency_ms)


publish_chaos_metrics()


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)
    path = request.url.path if request.url.path in KNOWN_PATHS else "other"
    start = time.perf_counter()
    status = 500  # if the handler crashes, count it as a server error
    IN_PROGRESS.inc()
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        IN_PROGRESS.dec()
        LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
        REQUESTS.labels(request.method, path, str(status)).inc()


async def inject_faults() -> None:
    """Dependency that simulates slowness/failures for chaos experiments."""
    if chaos.latency_ms:
        await asyncio.sleep(chaos.latency_ms / 1000)
    if random.random() < chaos.error_rate:
        raise HTTPException(status_code=500, detail="injected failure (chaos)")


@app.get("/orders", dependencies=[Depends(inject_faults)])
async def list_orders():
    await asyncio.sleep(random.uniform(0.01, 0.08))  # simulate a DB read
    return {"count": len(orders), "orders": list(orders.values())[-20:]}


@app.post("/orders", status_code=201, dependencies=[Depends(inject_faults)])
async def create_order(order: OrderIn):
    await asyncio.sleep(random.uniform(0.02, 0.12))  # simulate a DB write
    if len(orders) >= MAX_ORDERS:
        orders.pop(next(iter(orders)))  # evict oldest
    order_id = str(uuid.uuid4())
    orders[order_id] = {"id": order_id, **order.model_dump()}
    return orders[order_id]


@app.get("/health")
async def health():
    """Liveness: the process is up."""
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    """Readiness: the service can take traffic (extend with dependency checks)."""
    return {"status": "ready"}


@app.get("/chaos")
async def get_chaos():
    return chaos.model_dump() | {"enabled": CHAOS_ENABLED}


@app.post("/chaos")
async def set_chaos(config: ChaosConfig):
    if not CHAOS_ENABLED:
        raise HTTPException(status_code=403, detail="chaos endpoint disabled")
    chaos.error_rate = config.error_rate
    chaos.latency_ms = config.latency_ms
    publish_chaos_metrics()
    return chaos.model_dump()


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
