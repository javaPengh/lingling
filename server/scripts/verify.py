"""后端自测脚本。

验证建表、种子数据、DAO、学习闭环、记忆写回、观察面板和报告聚合。
"""

from __future__ import annotations

import sqlite3

from server.dao.connection import create_connection
from server.dao.question_dao import list_questions
from server.dao.student_dao import list_students
from server.models.schemas import LearningTurnRequest
from server.scripts.seed import seed_database
from server.services.observer import get_observer_session
from server.services.orchestrator import finish_session, handle_learning_turn, start_session
from server.services.reporting import get_student_report


def main() -> None:
    """运行完整后端验收流程。"""

    db = create_connection(":memory:")
    seed_database(db)
    _verify_counts(db)
    _verify_foreign_keys(db)
    _verify_student_list(db)
    session = start_session(db, "stu_001")
    turn1 = handle_learning_turn(
        db,
        LearningTurnRequest(
            session_id=session.session_id,
            student_id="stu_001",
            question_id="q_001",
            student_input="最小值是 1。",
            student_answer="1",
        ),
    )
    assert turn1.state == "confused", turn1
    assert turn1.is_correct is False, turn1
    turn2 = handle_learning_turn(
        db,
        LearningTurnRequest(
            session_id=session.session_id,
            student_id="stu_001",
            question_id="q_001",
            student_input="啊？还要分情况吗…我没懂对称轴跟区间有什么关系。",
        ),
    )
    assert turn2.state == "confused", turn2
    assert turn2.visual_aid_used == "function_graph", turn2
    turn3 = handle_learning_turn(
        db,
        LearningTurnRequest(
            session_id=session.session_id,
            student_id="stu_001",
            question_id="q_001",
            student_input="还是不会……这种含参的我每次都搞不定，我太笨了，算了吧。",
        ),
    )
    assert turn3.state == "frustrated", turn3
    assert turn3.care_triggered is True, turn3
    assert "small_step" in turn3.strategy, turn3
    turn4 = handle_learning_turn(
        db,
        LearningTurnRequest(
            session_id=session.session_id,
            student_id="stu_001",
            question_id="q_001",
            student_input="哦……那就是 f(0)=1！",
            student_answer="f(0)=1",
        ),
    )
    assert turn4.state == "stable", turn4
    assert turn4.is_correct is True, turn4

    finished = finish_session(db, session.session_id)
    assert finished.event_count == 4, finished
    assert finished.review_tasks, finished
    observer = get_observer_session(db, session.session_id)
    assert len(observer.events) == 4, observer
    assert observer.review_tasks, observer
    report = get_student_report(db, "stu_001")
    assert report.review_tasks, report
    print("verify ok: seed, DAO, learning loop, memory writeback, observer, report")


def _verify_counts(db: sqlite3.Connection) -> None:
    expected = {
        "student": 3,
        "student_profile": 3,
        "knowledge_point": 9,
        "student_knowledge": 13,
        "question": 7,
        "question_knowledge": 10,
    }
    for table, count in expected.items():
        row = db.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
        assert row["count"] == count, (table, row["count"], count)
    assert len(list_questions(db)) == 7


def _verify_foreign_keys(db: sqlite3.Connection) -> None:
    problems = db.execute("PRAGMA foreign_key_check").fetchall()
    assert problems == [], problems


def _verify_student_list(db: sqlite3.Connection) -> None:
    students = list_students(db)
    assert [student.id for student in students] == ["stu_001", "stu_003", "stu_002"]
    assert students[0].profile_label


if __name__ == "__main__":
    main()
