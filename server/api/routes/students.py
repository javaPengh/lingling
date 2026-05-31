"""学生相关 HTTP 路由。

当前 V0.1 登录即选择预置学生，因此本域只暴露学生列表。
"""

import sqlite3

from fastapi import APIRouter, Depends

from server.api.deps import get_db
from server.models.schemas import StudentsListResponse
from server.services.students import get_students


router = APIRouter(tags=["students"])


@router.get("/students", response_model=StudentsListResponse)
def list_students_endpoint(db: sqlite3.Connection = Depends(get_db)) -> StudentsListResponse:
    """返回可选择的预置学生卡片数据。"""

    return get_students(db)
