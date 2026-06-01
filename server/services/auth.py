"""登录认证与角色分流服务。

负责校验账号密码，并返回学生、家长、老师对应的前端目标页面和学生范围。
"""

import sqlite3

from server.core.enums import AccountRole
from server.core.security import verify_password
from server.dao.account_dao import get_account_by_login_identifier, list_students_for_account
from server.dao.student_dao import get_student_summary
from server.models.entities import Account
from server.models.schemas import AccountSummary, LoginRequest, LoginResponse, StudentSummary


def login_with_password(connection: sqlite3.Connection, credentials: LoginRequest) -> LoginResponse | None:
    """校验账号密码，成功时返回角色分流结果；失败时返回 None。"""

    account = get_account_by_login_identifier(connection, credentials.account.strip())
    if account is None:
        return None
    if not verify_password(credentials.password, account.password_hash):
        return None

    students = _students_for_login(connection, account)
    return LoginResponse(
        account=_account_summary(account),
        students=students,
        landing_page=_landing_page(account.role),
    )


def _students_for_login(connection: sqlite3.Connection, account: Account) -> list[StudentSummary]:
    """根据账号角色查询登录后可进入或可查看的学生范围。"""

    if account.role == AccountRole.STUDENT:
        if account.student_id is None:
            return []
        student = get_student_summary(connection, account.student_id)
        return [student] if student else []
    return list_students_for_account(connection, account.id)


def _landing_page(role: AccountRole) -> str:
    """把账号角色映射为前端登录成功后的目标页面。"""

    if role == AccountRole.STUDENT:
        return "student_learning"
    if role == AccountRole.PARENT:
        return "parent_report"
    return "teacher_report"


def _account_summary(account: Account) -> AccountSummary:
    """把账号实体映射为不含密码哈希的 API 摘要。"""

    return AccountSummary(
        id=account.id,
        username=account.username,
        role=account.role,
        display_name=account.display_name,
        student_id=account.student_id,
    )
