from fastapi import APIRouter, HTTPException, status

from app.services.health_service import HealthService

router = APIRouter(tags=["health"])


@router.get("/health", summary="Verifica a saúde da API")
def health_check() -> dict[str, str]:
    try:
        HealthService().check()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dependência de banco de dados indisponível",
        ) from exc
    return {"status": "ok", "database": "ok"}
