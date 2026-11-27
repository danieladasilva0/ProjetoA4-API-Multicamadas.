from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.routes.health import router as health_router
from app.api.routes.records import router as records_router
from app.core.logging import configure_logging
from app.middleware.metrics import MetricsLoggingMiddleware
from app.repositories.record_repository import RecordRepository

configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    RecordRepository().initialize()
    yield


app = FastAPI(
    title="API de Gerenciamento — Projeto A4",
    description="CRUD de registros com FastAPI, SQLite e métricas.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(MetricsLoggingMiddleware)
app.include_router(health_router)
app.include_router(records_router)


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
