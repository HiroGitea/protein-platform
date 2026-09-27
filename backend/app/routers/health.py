from __future__ import annotations

from fastapi import APIRouter

from app.engines import ENGINES
from app.gpu import get_gpu_info
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """前端启动时调一次：显卡在不在、每个引擎就没就绪、缺什么。"""
    return HealthResponse(
        gpu=get_gpu_info(),
        engines=[e.status() for e in ENGINES.values()],
    )
