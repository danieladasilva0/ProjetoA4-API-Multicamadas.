from app.core.database import get_connection


class HealthRepository:
    """Confere a conectividade do SQLite sem alterar dados da aplicação."""

    def check_database(self) -> bool:
        with get_connection() as connection:
            result = connection.execute("SELECT 1").fetchone()
        return result[0] == 1
