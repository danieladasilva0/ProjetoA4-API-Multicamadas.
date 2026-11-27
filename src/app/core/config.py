import os
from pathlib import Path


def database_path() -> Path:
    """Retorna o caminho configurável do arquivo SQLite."""
    return Path(os.getenv("DATABASE_PATH", "/tmp/projeto-a4.sqlite3"))
