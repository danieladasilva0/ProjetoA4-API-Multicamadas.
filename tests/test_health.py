import anyio
import httpx

from app.main import app
from app.repositories import health_repository


async def _get(path: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(path)


def request(path: str) -> httpx.Response:
    return anyio.run(_get, path)


def test_health_checks_sqlite(tmp_path, monkeypatch):
    monkeypatch.setattr(
        health_repository,
        "database_path",
        lambda: tmp_path / "health.sqlite3",
    )
    response = request("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_metrics_endpoint_is_available(tmp_path, monkeypatch):
    monkeypatch.setattr(
        health_repository,
        "database_path",
        lambda: tmp_path / "metrics.sqlite3",
    )
    request("/health")
    response = request("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text


def test_http_error_metrics_use_route_templates(tmp_path, monkeypatch):
    monkeypatch.setattr(
        health_repository,
        "database_path",
        lambda: tmp_path / "errors.sqlite3",
    )
    assert request("/does-not-exist").status_code == 404

    def unavailable_database():
        raise OSError("database unavailable")

    monkeypatch.setattr(health_repository, "database_path", unavailable_database)
    assert request("/health").status_code == 503
    metrics = request("/metrics").text
    assert 'path="__unmatched__",status="404"' in metrics
    assert 'path="/health",status="503"' in metrics
