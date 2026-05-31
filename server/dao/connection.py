from pathlib import Path
import sqlite3

from server.core.config import SERVER_DIR, settings


SCHEMA_PATH = SERVER_DIR / "db" / "schema.sql"


def create_connection(path: str | Path | None = None) -> sqlite3.Connection:
    database_path = str(path or settings.database_path)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    initialize_database(connection)
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(schema)
    connection.commit()
