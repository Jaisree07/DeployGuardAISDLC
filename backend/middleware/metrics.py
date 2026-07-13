import time

from starlette.middleware.base import BaseHTTPMiddleware

from backend.monitoring.prometheus import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    API_ERRORS,
)

from backend.telemetry.runtime import update_system_metrics


class MetricsMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        start_time = time.time()

        try:
            response = await call_next(request)

            duration = time.time() - start_time

            # Total Request Count
            REQUEST_COUNT.labels(
                request.method,
                request.url.path
            ).inc()

            # Request Latency
            REQUEST_LATENCY.labels(
                request.method,
                request.url.path
            ).observe(duration)

            # HTTP Error Counter
            if response.status_code >= 400:
                API_ERRORS.labels(
                    request.method,
                    request.url.path,
                    str(response.status_code)
                ).inc()

            # Runtime Metrics
            update_system_metrics()

            return response

        except Exception:

            duration = time.time() - start_time

            REQUEST_COUNT.labels(
                request.method,
                request.url.path
            ).inc()

            REQUEST_LATENCY.labels(
                request.method,
                request.url.path
            ).observe(duration)

            API_ERRORS.labels(
                request.method,
                request.url.path,
                "500"
            ).inc()

            update_system_metrics()

            raise