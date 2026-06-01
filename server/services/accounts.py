"""账号业务服务。

封装 MVP 预置账号列表与账号可查看学生范围的角色判断。
"""

import sqlite3

from server.core.enums import AccountRole
from server.dao.account_dao import get_account, list_accounts, list_students_for_account
from server.dao.student_dao import get_student_summary
from server.models.entities import Account
from server.models.schemas import AccountStudentsResponse, AccountSummary, AccountsListResponse, StudentSummary


def get_accounts(connection: sqlite3.Connection) -> AccountsListResponse:
    """返回登录入口可选择的预置账号列表。"""

    return AccountsListResponse(accounts=list_accounts(connection))


def get_account_students(connection: sqlite3.Connection, account_id: str) -> AccountStudentsResponse | None:
    """返回指定账号可查看或可进入的学生列表；账号不存在时返回 None。"""

    account = get_account(connection, account_id)
    if account is None:
        return None

    if account.role == AccountRole.STUDENT:
        students = _student_account_students(connection, account)
    else:
        students = list_students_for_account(connection, account.id)

    return AccountStudentsResponse(account=_account_summary(account), students=students)


def _student_account_students(connection: sqlite3.Connection, account: Account) -> list[StudentSummary]:
    """查询学生账号对应的本人学生摘要。"""

    if account.student_id is None:
        return []
    student = get_student_summary(connection, account.student_id)
    return [student] if student else []


def _account_summary(account: Account) -> AccountSummary:
    """把账号实体映射为 API 账号摘要。"""

    return AccountSummary(
        id=account.id,
        username=account.username,
        role=account.role,
        display_name=account.display_name,
        student_id=account.student_id,
    )
