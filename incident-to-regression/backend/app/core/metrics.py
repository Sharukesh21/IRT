"""Prometheus and application runtime metrics registry."""

import time
from collections import defaultdict
from typing import Any
from fastapi import APIRouter, Response

router = APIRouter(tags=["Metrics"])

# In-memory metrics counters and histograms
_metrics = {
    "http_requests_total": defaultdict(int),
    "http_request_duration_seconds": defaultdict(float),
    "incidents_ingested_total": 0,
    "ci_orchestrations_total": 0,
    "regression_runs_total": 0,
    "regression_escapes_total": 0,
}


def record_http_request(method: str, path: str, status_code: int, duration_sec: float) -> None:
    """Record HTTP request statistics."""
    key = f'method="{method}",path="{path}",status="{status_code}"'
    _metrics["http_requests_total"][key] += 1
    _metrics["http_request_duration_seconds"][key] += duration_sec


def increment_metric(name: str, count: int = 1) -> None:
    """Increment a registered counter."""
    if name in _metrics and isinstance(_metrics[name], int):
        _metrics[name] += count


@router.get("/metrics")
async def get_metrics() -> Response:
    """Expose Prometheus-compatible metrics endpoint."""
    lines: list[str] = [
        "# HELP http_requests_total Total number of HTTP requests processed.",
        "# TYPE http_requests_total counter",
    ]
    for labels, count in _metrics["http_requests_total"].items():
        lines.append(f"http_requests_total{{{labels}}} {count}")

    lines.extend([
        "# HELP http_request_duration_seconds_total Total processing time in seconds.",
        "# TYPE http_request_duration_seconds_total counter",
    ])
    for labels, duration in _metrics["http_request_duration_seconds"].items():
        lines.append(f"http_request_duration_seconds_total{{{labels}}} {duration:.4f}")

    lines.extend([
        "# HELP incidents_ingested_total Total external and simulated incidents ingested.",
        "# TYPE incidents_ingested_total counter",
        f"incidents_ingested_total {_metrics['incidents_ingested_total']}",
        "# HELP ci_orchestrations_total Total CI/CD orchestrations triggered.",
        "# TYPE ci_orchestrations_total counter",
        f"ci_orchestrations_total {_metrics['ci_orchestrations_total']}",
        "# HELP regression_escapes_total Total detected regression escapes.",
        "# TYPE regression_escapes_total counter",
        f"regression_escapes_total {_metrics['regression_escapes_total']}",
    ])

    return Response(content="\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")
