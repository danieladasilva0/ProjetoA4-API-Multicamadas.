import anyio
import httpx

from app.core import database
from app.main import app


async def _request(
    method: str, path: str, payload: dict | None = None
) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        return await client.request(method, path, json=payload)


def request(
    method: str, path: str, payload: dict | None = None
) -> httpx.Response:
    return anyio.run(_request, method, path, payload)


def use_test_database(tmp_path, monkeypatch, filename: str = "test.sqlite3") -> None:
    monkeypatch.setattr(database, "database_path", lambda: tmp_path / filename)


def test_health_checks_sqlite(tmp_path, monkeypatch):
    use_test_database(tmp_path, monkeypatch, "health.sqlite3")
    response = request("GET", "/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_records_crud_persists_to_sqlite(tmp_path, monkeypatch):
    use_test_database(tmp_path, monkeypatch, "records.sqlite3")
    payload = {"titulo": "Entrega A4", "descricao": "API multicamadas", "ativo": True}

    created = request("POST", "/registros", payload)
    assert created.status_code == 201
    record = created.json()
    assert record == {"id": 1, **payload}

    assert request("GET", "/registros").json() == [record]
    assert request("GET", "/registros/1").json() == record

    updated_payload = {
        "titulo": "Entrega concluída",
        "descricao": "Testes feitos",
        "ativo": False,
    }
    updated = request("PUT", "/registros/1", updated_payload)
    assert updated.status_code == 200
    assert updated.json() == {"id": 1, **updated_payload}

    deleted = request("DELETE", "/registros/1")
    assert deleted.status_code == 200
    assert deleted.json() == {"mensagem": "Registro removido com sucesso."}
    assert request("GET", "/registros").json() == []
    assert request("GET", "/registros/1").status_code == 404


def test_records_validate_blank_title_and_missing_ids(tmp_path, monkeypatch):
    use_test_database(tmp_path, monkeypatch, "validation.sqlite3")
    assert request("POST", "/registros", {"titulo": "  "}).status_code == 400
    assert request(
        "PUT", "/registros/404", {"titulo": "Atualização"}
    ).status_code == 404
    assert request("DELETE", "/registros/404").status_code == 404


def test_metrics_endpoint_is_available(tmp_path, monkeypatch):
    use_test_database(tmp_path, monkeypatch, "metrics.sqlite3")
    request("GET", "/health")
    response = request("GET", "/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text


def test_http_error_metrics_use_route_templates(tmp_path, monkeypatch):
    use_test_database(tmp_path, monkeypatch, "errors.sqlite3")
    assert request("GET", "/does-not-exist").status_code == 404

    def unavailable_database():
        raise OSError("database unavailable")

    monkeypatch.setattr(database, "database_path", unavailable_database)
    assert request("GET", "/health").status_code == 503
    metrics = request("GET", "/metrics").text
    assert 'path="__unmatched__",status="404"' in metrics
    assert 'path="/health",status="503"' in metrics
