"""
API Latency Logging Middleware

Logs request/response latency for all API calls.
Flags slow requests (>1s) for monitoring.
Logs are structured for P50/P95/P99 percentile calculation.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Threshold for slow request warning (in seconds)
SLOW_REQUEST_THRESHOLD = 1.0


class LatencyLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log API request latency.

    Logs include:
    - method: HTTP method
    - path: Request path
    - status_code: Response status code
    - latency_ms: Request duration in milliseconds
    - slow: Boolean flag if request exceeded threshold

    Example log output:
    {"method": "GET", "path": "/cases", "status_code": 200, "latency_ms": 45.2, "slow": false}
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        start_time = time.perf_counter()

        # Process the request
        response = await call_next(request)

        # Calculate latency
        end_time = time.perf_counter()
        latency_seconds = end_time - start_time
        latency_ms = latency_seconds * 1000

        # Determine if request is slow
        is_slow = latency_seconds > SLOW_REQUEST_THRESHOLD

        # Build log data
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(latency_ms, 2),
            "slow": is_slow,
        }

        # Add query params if present (for debugging)
        if request.url.query:
            log_data["query"] = request.url.query

        # Log at appropriate level
        if is_slow:
            logger.warning(
                f"SLOW_REQUEST: {log_data['method']} {log_data['path']} "
                f"took {log_data['latency_ms']}ms",
                extra={"latency_data": log_data}
            )
        else:
            logger.info(
                f"API_LATENCY: {log_data['method']} {log_data['path']} "
                f"{log_data['latency_ms']}ms",
                extra={"latency_data": log_data}
            )

        # Add latency header for debugging (optional)
        response.headers["X-Response-Time"] = f"{latency_ms:.2f}ms"

        return response


def get_latency_middleware() -> type:
    """
    Factory function to get LatencyLoggingMiddleware class.

    Returns:
        LatencyLoggingMiddleware class
    """
    return LatencyLoggingMiddleware
