"""题库与题目-知识点关联 DAO。

负责 `question` 和 `question_knowledge` 两张表的读写与 JSON 字段转换。
"""

import sqlite3

from server.dao.helpers import json_text, parse_json
from server.models.entities import Question, QuestionKnowledge


def upsert_question(connection: sqlite3.Connection, question: Question) -> None:
    """插入或更新一道预置题目。"""

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
    """按题目 ID 查询题目。"""

    row = connection.execute("SELECT * FROM question WHERE id = ?", (question_id,)).fetchone()
    return _question_from_row(row) if row else None


def list_questions(connection: sqlite3.Connection) -> list[Question]:
    """列出全部题目。"""

    rows = connection.execute("SELECT * FROM question ORDER BY id ASC").fetchall()
    return [_question_from_row(row) for row in rows]


def upsert_question_knowledge(connection: sqlite3.Connection, record: QuestionKnowledge) -> None:
    """插入或更新题目与知识点的关联。"""

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
    """查询一道题关联的知识点 ID 列表。"""

    rows = connection.execute(
        """
        SELECT knowledge_point_id FROM question_knowledge
        WHERE question_id = ?
        ORDER BY id ASC
        """,
        (question_id,),
    ).fetchall()
    return [row["knowledge_point_id"] for row in rows]
