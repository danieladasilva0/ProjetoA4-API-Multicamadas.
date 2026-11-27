from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.routes.health import router as health_router
from app.core.logging import configure_logging
from app.middleware.metrics import MetricsLoggingMiddleware

configure_logging()

app = FastAPI(
    title="Projeto A4 — API Multicamadas",
    description="API de exemplo organizada em camadas, com health check e métricas.",
    version="1.0.0",
)
app.add_middleware(MetricsLoggingMiddleware)
app.include_router(health_router)


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
