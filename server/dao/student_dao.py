import sqlite3

from server.dao.helpers import json_text, parse_json
from server.models.entities import Student, StudentKnowledge, StudentProfile
from server.models.schemas import StudentSummary


def upsert_student(connection: sqlite3.Connection, student: Student) -> None:
    connection.execute(
        """
        INSERT INTO student (id, name, grade, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          name=excluded.name,
          grade=excluded.grade,
          created_at=excluded.created_at
        """,
        (student.id, student.name, student.grade, student.created_at),
    )


def get_student(connection: sqlite3.Connection, student_id: str) -> Student | None:
    row = connection.execute("SELECT * FROM student WHERE id = ?", (student_id,)).fetchone()
    return Student.model_validate(dict(row)) if row else None


def list_students(connection: sqlite3.Connection) -> list[StudentSummary]:
    rows = connection.execute(
        """
        SELECT s.id, s.name, s.grade, p.learning_summary
        FROM student s
        LEFT JOIN student_profile p ON p.student_id = s.id
        ORDER BY s.created_at ASC
        """
    ).fetchall()
    summaries: list[StudentSummary] = []
    for row in rows:
        learning_summary = row["learning_summary"] or ""
        profile_label = None
        if learning_summary:
            profile_label = learning_summary.replace("，", "。").replace(",", "。").split("。")[0]
        summaries.append(
            StudentSummary(id=row["id"], name=row["name"], grade=row["grade"], profile_label=profile_label)
        )
    return summaries


def count_students(connection: sqlite3.Connection) -> int:
    row = connection.execute("SELECT COUNT(*) AS count FROM student").fetchone()
    return int(row["count"])


def upsert_student_profile(connection: sqlite3.Connection, profile: StudentProfile) -> None:
    connection.execute(
        """
        INSERT INTO student_profile (
          id, student_id, weak_points, recent_states, effective_strategies,
          learning_summary, total_sessions, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          student_id=excluded.student_id,
          weak_points=excluded.weak_points,
          recent_states=excluded.recent_states,
          effective_strategies=excluded.effective_strategies,
          learning_summary=excluded.learning_summary,
          total_sessions=excluded.total_sessions,
          updated_at=excluded.updated_at
        """,
        (
            profile.id,
            profile.student_id,
            json_text(profile.weak_points),
            json_text(profile.recent_states),
            json_text(profile.effective_strategies),
            profile.learning_summary,
            profile.total_sessions,
            profile.updated_at,
        ),
    )


def _profile_from_row(row: sqlite3.Row) -> StudentProfile:
    data = dict(row)
    data["weak_points"] = parse_json(data.pop("weak_points"), [])
    data["recent_states"] = parse_json(data.pop("recent_states"), [])
    data["effective_strategies"] = parse_json(data.pop("effective_strategies"), [])
    return StudentProfile.model_validate(data)


def get_student_profile(connection: sqlite3.Connection, student_id: str) -> StudentProfile | None:
    row = connection.execute("SELECT * FROM student_profile WHERE student_id = ?", (student_id,)).fetchone()
    return _profile_from_row(row) if row else None


def update_student_profile(connection: sqlite3.Connection, profile: StudentProfile) -> None:
    connection.execute(
        """
        UPDATE student_profile
        SET weak_points = ?,
            recent_states = ?,
            effective_strategies = ?,
            learning_summary = ?,
            total_sessions = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            json_text(profile.weak_points),
            json_text(profile.recent_states),
            json_text(profile.effective_strategies),
            profile.learning_summary,
            profile.total_sessions,
            profile.updated_at,
            profile.id,
        ),
    )


def upsert_student_knowledge(connection: sqlite3.Connection, record: StudentKnowledge) -> None:
    connection.execute(
        """
        INSERT INTO student_knowledge (
          id, student_id, knowledge_point_id, mastery, attempts, correct_count, last_practiced_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          student_id=excluded.student_id,
          knowledge_point_id=excluded.knowledge_point_id,
          mastery=excluded.mastery,
          attempts=excluded.attempts,
          correct_count=excluded.correct_count,
          last_practiced_at=excluded.last_practiced_at
        """,
        (
            record.id,
            record.student_id,
            record.knowledge_point_id,
            record.mastery,
            record.attempts,
            record.correct_count,
            record.last_practiced_at,
        ),
    )


def get_student_knowledge(
    connection: sqlite3.Connection, student_id: str, knowledge_point_id: str
) -> StudentKnowledge | None:
    row = connection.execute(
        """
        SELECT * FROM student_knowledge
        WHERE student_id = ? AND knowledge_point_id = ?
        """,
        (student_id, knowledge_point_id),
    ).fetchone()
    return StudentKnowledge.model_validate(dict(row)) if row else None


def list_student_knowledge(connection: sqlite3.Connection, student_id: str) -> list[StudentKnowledge]:
    rows = connection.execute(
        "SELECT * FROM student_knowledge WHERE student_id = ? ORDER BY mastery ASC",
        (student_id,),
    ).fetchall()
    return [StudentKnowledge.model_validate(dict(row)) for row in rows]


def list_weak_student_knowledge(
    connection: sqlite3.Connection, student_id: str, threshold: int = 60
) -> list[StudentKnowledge]:
    rows = connection.execute(
        """
        SELECT * FROM student_knowledge
        WHERE student_id = ? AND mastery < ?
        ORDER BY mastery ASC
        """,
        (student_id, threshold),
    ).fetchall()
    return [StudentKnowledge.model_validate(dict(row)) for row in rows]
