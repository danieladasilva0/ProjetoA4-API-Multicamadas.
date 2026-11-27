from app.models.record import RegistroBase
from app.repositories.record_repository import RecordRepository


class BlankTitleError(ValueError):
    """O título de um novo registro não pode conter apenas espaços."""


class RecordNotFoundError(LookupError):
    """O registro solicitado não existe."""


class RecordService:
    def __init__(self, repository: RecordRepository | None = None) -> None:
        self.repository = repository or RecordRepository()

    def create(self, registro: RegistroBase) -> dict:
        if not registro.titulo.strip():
            raise BlankTitleError("O título não pode estar em branco.")
        return self.repository.create(registro)

    def list_all(self) -> list[dict]:
        return self.repository.list_all()

    def get(self, registro_id: int) -> dict:
        registro = self.repository.get_by_id(registro_id)
        if registro is None:
            raise RecordNotFoundError("Registro não encontrado.")
        return registro

    def update(self, registro_id: int, registro: RegistroBase) -> dict:
        updated = self.repository.update(registro_id, registro)
        if updated is None:
            raise RecordNotFoundError("Registro não encontrado para atualização.")
        return updated

    def delete(self, registro_id: int) -> dict[str, str]:
        if not self.repository.delete(registro_id):
            raise RecordNotFoundError("Registro não encontrado para exclusão.")
        return {"mensagem": "Registro removido com sucesso."}
