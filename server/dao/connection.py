"""SQLite 连接与建表初始化。

DAO 层通过这里统一创建连接，确保外键校验和 schema 初始化一致。
"""

from pathlib import Path
import sqlite3

from server.core.config import SERVER_DIR, settings


SCHEMA_PATH = SERVER_DIR / "db" / "schema.sql"


def create_connection(path: str | Path | None = None) -> sqlite3.Connection:
    """创建 SQLite 连接，并自动执行建表脚本。"""

    database_path = str(path or settings.database_path)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    initialize_database(connection)
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    """在给定连接上执行 `server/db/schema.sql`。"""

    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    connection.executescript(schema)
    connection.commit()
