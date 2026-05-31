import sqlite3

from server.dao.helpers import json_text, parse_json
from server.models.entities import Question, QuestionKnowledge


def upsert_question(connection: sqlite3.Connection, question: Question) -> None:
    connection.execute(
        """
        INSERT INTO question (
          id, stem, standard_answer, solution, difficulty, typical_errors,
          visual_aid_type, visual_aid_spec
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          stem=excluded.stem,
          standard_answer=excluded.standard_answer,
          solution=excluded.solution,
          difficulty=excluded.difficulty,
          typical_errors=excluded.typical_errors,
          visual_aid_type=excluded.visual_aid_type,
          visual_aid_spec=excluded.visual_aid_spec
        """,
        (
            question.id,
            question.stem,
            question.standard_answer,
            question.solution,
            question.difficulty,
            json_text([error.model_dump() for error in question.typical_errors]),
            question.visual_aid_type,
            json_text(question.visual_aid_spec) if question.visual_aid_spec is not None else None,
        ),
    )


def _question_from_row(row: sqlite3.Row) -> Question:
    data = dict(row)
    data["typical_errors"] = parse_json(data.pop("typical_errors"), [])
    data["visual_aid_spec"] = parse_json(data.pop("visual_aid_spec"), None)
    return Question.model_validate(data)


def get_question(connection: sqlite3.Connection, question_id: str) -> Question | None:
    row = connection.execute("SELECT * FROM question WHERE id = ?", (question_id,)).fetchone()
    return _question_from_row(row) if row else None


def list_questions(connection: sqlite3.Connection) -> list[Question]:
    rows = connection.execute("SELECT * FROM question ORDER BY id ASC").fetchall()
    return [_question_from_row(row) for row in rows]


def upsert_question_knowledge(connection: sqlite3.Connection, record: QuestionKnowledge) -> None:
    connection.execute(
        """
        INSERT INTO question_knowledge (id, question_id, knowledge_point_id)
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          question_id=excluded.question_id,
          knowledge_point_id=excluded.knowledge_point_id
        """,
        (record.id, record.question_id, record.knowledge_point_id),
    )


def list_question_knowledge_ids(connection: sqlite3.Connection, question_id: str) -> list[str]:
    rows = connection.execute(
        """
        SELECT knowledge_point_id FROM question_knowledge
        WHERE question_id = ?
        ORDER BY id ASC
        """,
        (question_id,),
    ).fetchall()
    return [row["knowledge_point_id"] for row in rows]
