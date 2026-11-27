from fastapi import APIRouter, HTTPException, status

from app.models.record import RegistroBase, RegistroResponse
from app.services.record_service import (
    BlankTitleError,
    RecordNotFoundError,
    RecordService,
)

router = APIRouter(prefix="/registros", tags=["registros"])


@router.post(
    "",
    response_model=RegistroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um registro",
)
def create_record(registro: RegistroBase) -> dict:
    try:
        return RecordService().create(registro)
    except BlankTitleError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "",
    response_model=list[RegistroResponse],
    summary="Lista os registros",
)
def list_records() -> list[dict]:
    return RecordService().list_all()


@router.get(
    "/{registro_id}",
    response_model=RegistroResponse,
    summary="Busca um registro pelo ID",
)
def get_record(registro_id: int) -> dict:
    try:
        return RecordService().get(registro_id)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put(
    "/{registro_id}",
    response_model=RegistroResponse,
    summary="Atualiza um registro",
)
def update_record(registro_id: int, registro: RegistroBase) -> dict:
    try:
        return RecordService().update(registro_id, registro)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete(
    "/{registro_id}",
    summary="Exclui um registro",
)
def delete_record(registro_id: int) -> dict[str, str]:
    try:
        return RecordService().delete(registro_id)
    except RecordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
