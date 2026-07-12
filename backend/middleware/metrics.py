import time

from starlette.middleware.base import BaseHTTPMiddleware

from backend.monitoring.prometheus import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
)
from backend.telemetry.runtime import update_system_metrics


class MetricsMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        start_time = time.time()

        response = await call_next(request)

        duration = time.time() - start_time

        # Increment request counter
        REQUEST_COUNT.labels(
            request.method,
            request.url.path
        ).inc()

        # Record request latency
        REQUEST_LATENCY.labels(
            request.method,
            request.url.path
        ).observe(duration)

        # Update runtime system metrics
        update_system_metrics()

        return response