from time import perf_counter

from fastapi import Request
from loguru import logger
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total de requisições HTTP concluídas.",
    ("method", "path", "status"),
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Duração das requisições HTTP em segundos.",
    ("method", "path"),
)


def _route_label(request: Request) -> str:
    route = request.scope.get("route")
    return getattr(route, "path", None) or "__unmatched__"


class MetricsLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed = perf_counter() - started_at
            route = _route_label(request)
            REQUEST_COUNT.labels(request.method, route, "500").inc()
            REQUEST_LATENCY.labels(request.method, route).observe(elapsed)
            logger.bind(
                method=request.method,
                path=route,
                status_code=500,
                duration_seconds=round(elapsed, 6),
            ).exception("http_request_failed")
            raise

        elapsed = perf_counter() - started_at
        route = _route_label(request)
        REQUEST_COUNT.labels(request.method, route, str(response.status_code)).inc()
        REQUEST_LATENCY.labels(request.method, route).observe(elapsed)
        logger.bind(
            method=request.method,
            path=route,
            status_code=response.status_code,
            duration_seconds=round(elapsed, 6),
        ).info("http_request")
        return response
