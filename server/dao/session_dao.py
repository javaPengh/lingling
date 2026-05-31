"""会话与学习事件 DAO。

负责 `session` 和 `learning_event` 两张核心过程表的读写。
"""

import sqlite3

from server.dao.helpers import bool_to_int, int_to_bool, json_text, parse_json
from server.models.entities import LearningEvent, LearningSession


def insert_session(connection: sqlite3.Connection, session: LearningSession) -> None:
    """创建一条学习会话记录。"""

    connection.execute(
        """
        INSERT INTO session (id, student_id, started_at, ended_at, dominant_state, summary, event_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session.id,
            session.student_id,
            session.started_at,
            session.ended_at,
            session.dominant_state,
            session.summary,
            session.event_count,
        ),
    )


def get_session(connection: sqlite3.Connection, session_id: str) -> LearningSession | None:
    """按会话 ID 查询学习会话。"""

    row = connection.execute("SELECT * FROM session WHERE id = ?", (session_id,)).fetchone()
    return LearningSession.model_validate(dict(row)) if row else None


def update_session_finish(
    connection: sqlite3.Connection,
    session_id: str,
    ended_at: str,
    dominant_state: str | None,
    summary: str,
    event_count: int,
) -> None:
    """写入会话结束时间、主导状态、摘要和事件数量。"""

    connection.execute(
        """
        UPDATE session
        SET ended_at = ?, dominant_state = ?, summary = ?, event_count = ?
        WHERE id = ?
        """,
        (ended_at, dominant_state, summary, event_count, session_id),
    )


def next_event_sequence(connection: sqlite3.Connection, session_id: str) -> int:
    """计算某个会话内下一条学习事件序号。"""

    row = connection.execute(
        "SELECT COALESCE(MAX(sequence), 0) + 1 AS sequence FROM learning_event WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    return int(row["sequence"])


def insert_learning_event(connection: sqlite3.Connection, event: LearningEvent) -> None:
    """写入一轮结构化学习事件。"""

    connection.execute(
        """
        INSERT INTO learning_event (
          id, session_id, student_id, question_id, sequence, student_input, student_answer,
          is_correct, knowledge_point_ids, error_cause, error_detail, state, state_evidence,
          strategy, strategy_reason, care_triggered, visual_aid_used, tutor_response, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.id,
            event.session_id,
            event.student_id,
            event.question_id,
            event.sequence,
            event.student_input,
            event.student_answer,
            bool_to_int(event.is_correct),
            json_text(event.knowledge_point_ids),
            event.error_cause,
            event.error_detail,
            event.state,
            event.state_evidence,
            json_text(event.strategy),
            event.strategy_reason,
            bool_to_int(event.care_triggered) or 0,
            event.visual_aid_used,
            event.tutor_response,
            event.created_at,
        ),
    )


def _event_from_row(row: sqlite3.Row) -> LearningEvent:
    data = dict(row)
    data["is_correct"] = int_to_bool(data["is_correct"])
    data["care_triggered"] = bool(data["care_triggered"])
    data["knowledge_point_ids"] = parse_json(data.pop("knowledge_point_ids"), [])
    data["strategy"] = parse_json(data.pop("strategy"), [])
    return LearningEvent.model_validate(data)


def list_events_by_session(connection: sqlite3.Connection, session_id: str) -> list[LearningEvent]:
    """按会话顺序列出学习事件。"""

    rows = connection.execute(
        "SELECT * FROM learning_event WHERE session_id = ? ORDER BY sequence ASC",
        (session_id,),
    ).fetchall()
    return [_event_from_row(row) for row in rows]


def list_recent_events_by_student(
    connection: sqlite3.Connection, student_id: str, limit: int = 10
) -> list[LearningEvent]:
    """查询某个学生最近的学习事件。"""

    rows = connection.execute(
        """
        SELECT * FROM learning_event
        WHERE student_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (student_id, limit),
    ).fetchall()
    return [_event_from_row(row) for row in rows]


def list_recent_sessions_by_student(
    connection: sqlite3.Connection, student_id: str, limit: int = 2
) -> list[LearningSession]:
    """查询某个学生最近已结束的学习会话。"""

    rows = connection.execute(
        """
        SELECT * FROM session
        WHERE student_id = ? AND ended_at IS NOT NULL
        ORDER BY ended_at DESC
        LIMIT ?
        """,
        (student_id, limit),
    ).fetchall()
    return [LearningSession.model_validate(dict(row)) for row in rows]
