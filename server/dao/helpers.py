"""SQLite 字段转换辅助函数。

集中处理 JSON、布尔值和 Row 映射，避免各 DAO 重复写转换逻辑。
"""

from collections.abc import Iterable
import json
import sqlite3
from typing import Any, TypeVar


T = TypeVar("T")


def json_text(value: Any) -> str:
    """把 Python 值序列化为紧凑 JSON 文本。"""

    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def nullable_json_text(value: Any | None) -> str | None:
    """把可空 Python 值序列化为 JSON 文本。"""

    return None if value is None else json_text(value)


def parse_json(value: str | None, fallback: T) -> T:
    """解析 SQLite 中存储的 JSON 文本，空值返回 fallback。"""

    if value is None or value == "":
        return fallback
    return json.loads(value)


def bool_to_int(value: bool | None) -> int | None:
    """把 Python 布尔值映射为 SQLite 中的 1/0/NULL。"""

    if value is None:
        return None
    return 1 if value else 0


def int_to_bool(value: int | None) -> bool | None:
    """把 SQLite 中的 1/0/NULL 映射为 Python 布尔值。"""

    if value is None:
        return None
    return bool(value)


def row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """把单行 SQLite Row 转成普通 dict。"""

    return None if row is None else dict(row)


def rows_dict(rows: Iterable[sqlite3.Row]) -> list[dict[str, Any]]:
    """把多行 SQLite Row 转成普通 dict 列表。"""

    return [dict(row) for row in rows]
