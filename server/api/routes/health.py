from fastapi import APIRouter

from server.core.config import settings
from server.models.schemas import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(mode="live" if settings.llm_mode == "live" else "mock")
