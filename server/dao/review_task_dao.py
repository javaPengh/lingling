"""复习任务 DAO。

负责 `review_task` 表的写入和按学生/会话查询。
"""

import sqlite3

from server.models.entities import ReviewTask


def upsert_review_task(connection: sqlite3.Connection, task: ReviewTask) -> None:
    """插入或更新一条复习任务。"""

    connection.execute(
        """
        INSERT INTO review_task (
          id, student_id, knowledge_point_id, source_event_id, reason,
          recommended_question_id, status, due_date, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          source_event_id=excluded.source_event_id,
          reason=excluded.reason,
          recommended_question_id=excluded.recommended_question_id,
          status=excluded.status,
          due_date=excluded.due_date,
          created_at=excluded.created_at
        """,
        (
            task.id,
            task.student_id,
            task.knowledge_point_id,
            task.source_event_id,
            task.reason,
            task.recommended_question_id,
            task.status,
            task.due_date,
            task.created_at,
        ),
    )


def list_review_tasks_by_student(connection: sqlite3.Connection, student_id: str) -> list[ReviewTask]:
    """查询某个学生的复习任务。"""

    rows = connection.execute(
        """
        SELECT * FROM review_task
        WHERE student_id = ?
        ORDER BY created_at DESC
        """,
        (student_id,),
    ).fetchall()
    return [ReviewTask.model_validate(dict(row)) for row in rows]


def list_review_tasks_by_session(connection: sqlite3.Connection, session_id: str) -> list[ReviewTask]:
    """查询某个会话产生的复习任务。"""

    rows = connection.execute(
        """
        SELECT rt.*
        FROM review_task rt
        LEFT JOIN learning_event le ON le.id = rt.source_event_id
        WHERE le.session_id = ?
        ORDER BY rt.created_at DESC
        """,
        (session_id,),
    ).fetchall()
    return [ReviewTask.model_validate(dict(row)) for row in rows]
