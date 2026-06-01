"""登录认证 HTTP 路由。

提供账号密码登录接口，返回角色分流结果。
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from server.api.deps import get_db
from server.models.schemas import LoginRequest, LoginResponse
from server.services.auth import login_with_password


router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=LoginResponse)
def login_endpoint(credentials: LoginRequest, db: sqlite3.Connection = Depends(get_db)) -> LoginResponse:
    """校验账号密码，并返回登录后的角色目标页面和学生范围。"""

    response = login_with_password(db, credentials)
    if response is None:
        raise HTTPException(status_code=401, detail="Invalid account or password")
    return response
