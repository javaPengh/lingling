"""FastAPI 依赖注入工具。

本文件只放接口层需要的通用依赖，例如数据库连接生命周期管理。
"""

from collections.abc import Iterator
import sqlite3

from server.dao.connection import create_connection


def get_db() -> Iterator[sqlite3.Connection]:
    """为每个 HTTP 请求创建 SQLite 连接，并在请求结束后关闭。"""

    connection = create_connection()
    try:
        yield connection
    finally:
        connection.close()
