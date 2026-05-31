"""学习闭环 HTTP 路由。

本文件只接收请求、调用编排服务并返回响应；具体业务逻辑在 services 层。
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from server.api.deps import get_db
from server.models.schemas import (
    FinishSessionResponse,
    LearningTurnRequest,
    LearningTurnResponse,
    StartSessionRequest,
    StartSessionResponse,
)
from server.services.orchestrator import finish_session, handle_learning_turn, start_session


router = APIRouter(prefix="/learning", tags=["learning"])


@router.post("/sessions", response_model=StartSessionResponse)
def start_session_endpoint(
    request: StartSessionRequest, db: sqlite3.Connection = Depends(get_db)
) -> StartSessionResponse:
    """创建学习会话并返回开场上下文。"""

    try:
        return start_session(db, request.student_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/turns", response_model=LearningTurnResponse)
def learning_turn_endpoint(
    request: LearningTurnRequest, db: sqlite3.Connection = Depends(get_db)
) -> LearningTurnResponse:
    """处理一轮学生输入，并返回灵灵回应与决策结果。"""

    try:
        return handle_learning_turn(db, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/finish", response_model=FinishSessionResponse)
def finish_session_endpoint(session_id: str, db: sqlite3.Connection = Depends(get_db)) -> FinishSessionResponse:
    """结束会话，触发长期记忆写回和复习任务生成。"""

    try:
        return finish_session(db, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
