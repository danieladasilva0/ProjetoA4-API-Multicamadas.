from app.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, repository: HealthRepository | None = None) -> None:
        self.repository = repository or HealthRepository()

    def check(self) -> None:
        if not self.repository.check_database():
            raise RuntimeError("SQLite não respondeu à verificação")
