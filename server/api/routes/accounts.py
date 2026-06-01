"""账号相关 HTTP 路由。

提供 MVP 预置账号列表，以及账号可查看学生范围查询。
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from server.api.deps import get_db
from server.models.schemas import AccountStudentsResponse, AccountsListResponse
from server.services.accounts import get_account_students, get_accounts


router = APIRouter(tags=["accounts"])


@router.get("/accounts", response_model=AccountsListResponse)
def list_accounts_endpoint(db: sqlite3.Connection = Depends(get_db)) -> AccountsListResponse:
    """返回登录入口可选择的预置账号列表。"""

    return get_accounts(db)


@router.get("/accounts/{account_id}/students", response_model=AccountStudentsResponse)
def account_students_endpoint(
    account_id: str, db: sqlite3.Connection = Depends(get_db)
) -> AccountStudentsResponse:
    """返回指定账号可查看或可进入的学生列表。"""

    response = get_account_students(db, account_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return response
