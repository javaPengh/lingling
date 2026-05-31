"""健康检查路由。

用于前端确认后端服务可用，以及当前 LLM 运行模式。
"""

from fastapi import APIRouter

from server.core.config import settings
from server.models.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """返回后端健康状态和 mock/live 模式。"""

    return HealthResponse(mode="live" if settings.llm_mode == "live" else "mock")
