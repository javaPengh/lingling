from collections.abc import Iterable
import json
import sqlite3
from typing import Any, TypeVar


T = TypeVar("T")


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def nullable_json_text(value: Any | None) -> str | None:
    return None if value is None else json_text(value)


def parse_json(value: str | None, fallback: T) -> T:
    if value is None or value == "":
        return fallback
    return json.loads(value)


def bool_to_int(value: bool | None) -> int | None:
    if value is None:
        return None
    return 1 if value else 0


def int_to_bool(value: int | None) -> bool | None:
    if value is None:
        return None
    return bool(value)


def row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return None if row is None else dict(row)


def rows_dict(rows: Iterable[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]
