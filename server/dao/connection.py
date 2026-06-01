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
    _ensure_account_login_columns(connection)
    connection.commit()


def _ensure_account_login_columns(connection: sqlite3.Connection) -> None:
    """为旧本地库补齐账号登录字段，避免已有 account 表无法升级。"""

    columns = {row["name"] for row in connection.execute("PRAGMA table_info(account)").fetchall()}
    if "username" not in columns:
        connection.execute("ALTER TABLE account ADD COLUMN username TEXT")
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_account_username ON account(username)")
    if "password_hash" not in columns:
        connection.execute("ALTER TABLE account ADD COLUMN password_hash TEXT")
