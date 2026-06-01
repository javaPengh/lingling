"""后端自测脚本。

验证建表、种子数据、DAO、学习闭环、记忆写回、观察面板和报告聚合。
"""

from __future__ import annotations

import sqlite3

from server.dao.account_dao import count_account_students, count_accounts, count_accounts_missing_credentials, list_accounts
from server.dao.connection import create_connection
from server.dao.question_dao import list_questions
from server.dao.student_dao import list_students
from server.models.schemas import LearningTurnRequest, LoginRequest
from server.scripts.seed import seed_database
from server.services.auth import login_with_password
from server.services.accounts import get_account_students
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
    _verify_account_access(db)
    _verify_login_routing(db)
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
    print("verify ok: seed, accounts, login routing, DAO, learning loop, memory writeback, observer, report")


def _verify_counts(db: sqlite3.Connection) -> None:
    expected = {
        "student": 3,
        "account": 5,
        "account_student": 4,
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
    assert count_accounts(db) == 5
    assert count_account_students(db) == 4
    assert count_accounts_missing_credentials(db) == 0


def _verify_foreign_keys(db: sqlite3.Connection) -> None:
    problems = db.execute("PRAGMA foreign_key_check").fetchall()
    assert problems == [], problems


def _verify_student_list(db: sqlite3.Connection) -> None:
    students = list_students(db)
    assert [student.id for student in students] == ["stu_001", "stu_003", "stu_002"]
    assert students[0].profile_label


def _verify_account_access(db: sqlite3.Connection) -> None:
    """验证三角色预置账号与可查看学生范围。"""

    accounts = list_accounts(db)
    assert [account.id for account in accounts] == [
        "acc_stu_001",
        "acc_stu_002",
        "acc_stu_003",
        "acc_parent_001",
        "acc_teacher_001",
    ]
    assert [account.username for account in accounts] == [
        "xiaoyu",
        "xiaozhe",
        "xiaolin",
        "parent_xiaoyu",
        "teacher_wang",
    ]
    assert [account.role for account in accounts] == ["student", "student", "student", "parent", "teacher"]

    student_account = get_account_students(db, "acc_stu_001")
    assert student_account is not None
    assert [student.id for student in student_account.students] == ["stu_001"]

    parent_account = get_account_students(db, "acc_parent_001")
    assert parent_account is not None
    assert [student.id for student in parent_account.students] == ["stu_001"]

    teacher_account = get_account_students(db, "acc_teacher_001")
    assert teacher_account is not None
    assert [student.id for student in teacher_account.students] == ["stu_001", "stu_002", "stu_003"]


def _verify_login_routing(db: sqlite3.Connection) -> None:
    """验证账号密码登录后的角色分流结果。"""

    student_login = login_with_password(db, LoginRequest(account="xiaoyu", password="123456"))
    assert student_login is not None
    assert student_login.account.role == "student"
    assert student_login.landing_page == "student_learning"
    assert [student.id for student in student_login.students] == ["stu_001"]

    parent_login = login_with_password(db, LoginRequest(account="parent_xiaoyu", password="123456"))
    assert parent_login is not None
    assert parent_login.account.role == "parent"
    assert parent_login.landing_page == "parent_report"
    assert [student.id for student in parent_login.students] == ["stu_001"]

    teacher_login = login_with_password(db, LoginRequest(account="teacher_wang", password="123456"))
    assert teacher_login is not None
    assert teacher_login.account.role == "teacher"
    assert teacher_login.landing_page == "teacher_report"
    assert [student.id for student in teacher_login.students] == ["stu_001", "stu_002", "stu_003"]

    invalid_login = login_with_password(db, LoginRequest(account="xiaoyu", password="wrong"))
    assert invalid_login is None


if __name__ == "__main__":
    main()
