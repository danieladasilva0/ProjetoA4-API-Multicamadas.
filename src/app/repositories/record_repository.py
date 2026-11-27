from app.core.database import get_connection
from app.models.record import RegistroBase


class RecordRepository:
    def initialize(self) -> None:
        with get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS registros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    descricao TEXT,
                    ativo BOOLEAN DEFAULT TRUE
                )
                """
            )

    def create(self, registro: RegistroBase) -> dict:
        self.initialize()
        with get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO registros (titulo, descricao, ativo) VALUES (?, ?, ?)",
                (registro.titulo, registro.descricao, registro.ativo),
            )
            row = connection.execute(
                "SELECT * FROM registros WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return dict(row)

    def list_all(self) -> list[dict]:
        self.initialize()
        with get_connection() as connection:
            rows = connection.execute("SELECT * FROM registros ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def get_by_id(self, registro_id: int) -> dict | None:
        self.initialize()
        with get_connection() as connection:
            row = connection.execute(
                "SELECT * FROM registros WHERE id = ?", (registro_id,)
            ).fetchone()
        return dict(row) if row is not None else None

    def update(self, registro_id: int, registro: RegistroBase) -> dict | None:
        self.initialize()
        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE registros
                SET titulo = ?, descricao = ?, ativo = ?
                WHERE id = ?
                """,
                (registro.titulo, registro.descricao, registro.ativo, registro_id),
            )
            if cursor.rowcount == 0:
                return None
            row = connection.execute(
                "SELECT * FROM registros WHERE id = ?", (registro_id,)
            ).fetchone()
        return dict(row)

    def delete(self, registro_id: int) -> bool:
        self.initialize()
        with get_connection() as connection:
            cursor = connection.execute(
                "DELETE FROM registros WHERE id = ?", (registro_id,)
            )
        return cursor.rowcount > 0
