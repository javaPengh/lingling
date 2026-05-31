from collections.abc import Iterator
import sqlite3

from server.dao.connection import create_connection


def get_db() -> Iterator[sqlite3.Connection]:
    connection = create_connection()
    try:
        yield connection
    finally:
        connection.close()
