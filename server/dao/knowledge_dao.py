import sqlite3

from server.models.entities import KnowledgePoint


def upsert_knowledge_point(connection: sqlite3.Connection, point: KnowledgePoint) -> None:
    connection.execute(
        """
        INSERT INTO knowledge_point (id, name, subject, chapter, parent_id)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          name=excluded.name,
          subject=excluded.subject,
          chapter=excluded.chapter,
          parent_id=excluded.parent_id
        """,
        (point.id, point.name, point.subject, point.chapter, point.parent_id),
    )


def get_knowledge_point(connection: sqlite3.Connection, point_id: str) -> KnowledgePoint | None:
    row = connection.execute("SELECT * FROM knowledge_point WHERE id = ?", (point_id,)).fetchone()
    return KnowledgePoint.model_validate(dict(row)) if row else None


def list_knowledge_points(connection: sqlite3.Connection) -> list[KnowledgePoint]:
    rows = connection.execute("SELECT * FROM knowledge_point ORDER BY id ASC").fetchall()
    return [KnowledgePoint.model_validate(dict(row)) for row in rows]
