"""四个工具的提交入口。统一模式：提交 -> 拿 job_id -> 轮询 /api/jobs/{id}。"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.engines import ENGINES
from app.jobs import job_manager
from app.schemas import (
    DiffDockRequest,
    FoldRequest,
    GenMolRequest,
    JobCreated,
    MMseqsRequest,
)

router = APIRouter(tags=["tools"])


def _submit(engine_name: str, params: dict[str, Any]) -> JobCreated:
    engine = ENGINES[engine_name]
    job = job_manager.submit(engine_name, params, engine.run)
    return JobCreated(job_id=job.id, status=job.status)


@router.post("/genmol/generate", response_model=JobCreated)
async def genmol_generate(req: GenMolRequest) -> JobCreated:
    return _submit("genmol", req.model_dump())


@router.post("/diffdock/dock", response_model=JobCreated)
async def diffdock_dock(req: DiffDockRequest) -> JobCreated:
    return _submit("diffdock", req.model_dump())


@router.post("/mmseqs/search", response_model=JobCreated)
async def mmseqs_search(req: MMseqsRequest) -> JobCreated:
    return _submit("mmseqs", req.model_dump())


@router.post("/fold/predict", response_model=JobCreated)
async def fold_predict(req: FoldRequest) -> JobCreated:
    return _submit("fold", req.model_dump())
