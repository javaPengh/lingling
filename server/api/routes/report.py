"""报告预览 HTTP 路由。

报告接口聚合学生画像、薄弱点、复习任务和近期事件，供教师/家长视角展示。
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from server.api.deps import get_db
from server.models.schemas import ReportResponse
from server.services.reporting import get_student_report


router = APIRouter(prefix="/report", tags=["report"])


@router.get("/students/{student_id}", response_model=ReportResponse)
def report_endpoint(student_id: str, db: sqlite3.Connection = Depends(get_db)) -> ReportResponse:
    """按学生 ID 返回报告预览数据。"""

    try:
        return get_student_report(db, student_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
