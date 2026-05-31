"""观察面板 HTTP 路由。

观察面板用于展示一场会话的记忆读取、状态识别、策略与写回结果。
"""

import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from server.api.deps import get_db
from server.models.schemas import ObserverSessionResponse
from server.services.observer import get_observer_session


router = APIRouter(prefix="/observer", tags=["observer"])


@router.get("/sessions/{session_id}", response_model=ObserverSessionResponse)
def observer_session_endpoint(
    session_id: str, db: sqlite3.Connection = Depends(get_db)
) -> ObserverSessionResponse:
    """按会话 ID 返回观察面板所需的决策链路数据。"""

    try:
        return get_observer_session(db, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
