"""账号与账号-学生关联 DAO。

负责 `account` 和 `account_student` 两张表的 SQLite 读写。
"""

import sqlite3

from server.models.entities import Account, AccountStudent
from server.models.schemas import AccountSummary, StudentSummary


def upsert_account(connection: sqlite3.Connection, account: Account) -> None:
    """插入或更新预置账号。"""

    connection.execute(
        """
        INSERT INTO account (id, username, password_hash, role, display_name, student_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
          username=excluded.username,
          password_hash=excluded.password_hash,
          role=excluded.role,
          display_name=excluded.display_name,
          student_id=excluded.student_id,
          created_at=excluded.created_at
        """,
        (
            account.id,
            account.username,
            account.password_hash,
            account.role,
            account.display_name,
            account.student_id,
            account.created_at,
        ),
    )


def upsert_account_student(connection: sqlite3.Connection, relation: AccountStudent) -> None:
    """插入或更新账号可查看学生的关联记录。"""

    connection.execute(
        """
        INSERT INTO account_student (id, account_id, student_id)
        VALUES (?, ?, ?)
        ON CONFLICT(account_id, student_id) DO UPDATE SET
          id=excluded.id
        """,
        (relation.id, relation.account_id, relation.student_id),
    )


def get_account(connection: sqlite3.Connection, account_id: str) -> Account | None:
    """按账号 ID 查询账号实体。"""

    row = connection.execute("SELECT * FROM account WHERE id = ?", (account_id,)).fetchone()
    return Account.model_validate(dict(row)) if row else None


def get_account_by_login_identifier(connection: sqlite3.Connection, identifier: str) -> Account | None:
    """按登录输入查询账号，兼容 username、账号 ID 和展示名。"""

    row = connection.execute(
        """
        SELECT * FROM account
        WHERE username = ? OR id = ? OR display_name = ?
        """,
        (identifier, identifier, identifier),
    ).fetchone()
    return Account.model_validate(dict(row)) if row else None


def list_accounts(connection: sqlite3.Connection) -> list[AccountSummary]:
    """列出登录入口可选择的预置账号。"""

    rows = connection.execute(
        """
        SELECT id, username, role, display_name, student_id
        FROM account
        ORDER BY created_at ASC, id ASC
        """
    ).fetchall()
    return [AccountSummary.model_validate(dict(row)) for row in rows]


def count_accounts(connection: sqlite3.Connection) -> int:
    """统计账号数量，用于判断是否需要补种账号数据。"""

    row = connection.execute("SELECT COUNT(*) AS count FROM account").fetchone()
    return int(row["count"])


def count_account_students(connection: sqlite3.Connection) -> int:
    """统计账号-学生关联数量，用于验证种子关系是否完整。"""

    row = connection.execute("SELECT COUNT(*) AS count FROM account_student").fetchone()
    return int(row["count"])


def count_accounts_missing_credentials(connection: sqlite3.Connection) -> int:
    """统计缺少 username 或 password_hash 的账号数量。"""

    row = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM account
        WHERE username IS NULL
           OR username = ''
           OR password_hash IS NULL
           OR password_hash = ''
        """
    ).fetchone()
    return int(row["count"])


def list_students_for_account(connection: sqlite3.Connection, account_id: str) -> list[StudentSummary]:
    """列出家长或老师账号通过关联表可查看的学生。"""

    rows = connection.execute(
        """
        SELECT s.id, s.name, s.grade, p.learning_summary
        FROM account_student a_s
        JOIN student s ON s.id = a_s.student_id
        LEFT JOIN student_profile p ON p.student_id = s.id
        WHERE a_s.account_id = ?
        ORDER BY a_s.id ASC
        """,
        (account_id,),
    ).fetchall()
    return [_student_summary_from_row(row) for row in rows]


def _student_summary_from_row(row: sqlite3.Row) -> StudentSummary:
    """把学生与画像查询结果映射为学生摘要 DTO。"""

    learning_summary = row["learning_summary"] or ""
    profile_label = None
    if learning_summary:
        profile_label = learning_summary.replace("，", "。").replace(",", "。").split("。")[0]
    return StudentSummary(id=row["id"], name=row["name"], grade=row["grade"], profile_label=profile_label)
