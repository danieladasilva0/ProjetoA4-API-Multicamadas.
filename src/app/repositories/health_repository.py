import sqlite3

from app.core.config import database_path


class HealthRepository:
    """Confere a conectividade do SQLite sem alterar dados da aplicação."""

    def check_database(self) -> bool:
        path = database_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path, timeout=2) as connection:
            result = connection.execute("SELECT 1").fetchone()
        return result == (1,)
