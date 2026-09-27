"""各工具的提交入口。统一模式：提交 -> 拿 job_id -> 轮询 /api/jobs/{id}。"""

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
    MolMimRequest,
)

router = APIRouter(tags=["tools"])


def _submit(engine_name: str, params: dict[str, Any]) -> JobCreated:
    engine = ENGINES[engine_name]
    job = job_manager.submit(engine_name, params, engine.run)
    return JobCreated(job_id=job.id, status=job.status)


@router.post("/genmol/generate", response_model=JobCreated)
async def genmol_generate(req: GenMolRequest) -> JobCreated:
    """GenMol 分子生成。local: 本地 89M 模型 / remote: NVIDIA NIM。"""
    return _submit("genmol", req.model_dump())


@router.post("/molmim/optimize", response_model=JobCreated)
async def molmim_optimize(req: MolMimRequest) -> JobCreated:
    """MolMIM 分子性质优化（CMA-ES）。默认走远程。"""
    return _submit("molmim", req.model_dump())


@router.post("/diffdock/dock", response_model=JobCreated)
async def diffdock_dock(req: DiffDockRequest) -> JobCreated:
    """DiffDock 分子对接。蛋白和配体先用 POST /api/files 上传。"""
    return _submit("diffdock", req.model_dump())


@router.post("/mmseqs/search", response_model=JobCreated)
async def mmseqs_search(req: MMseqsRequest) -> JobCreated:
    """MMseqs2 序列搜索。仅本地，需先建库。"""
    return _submit("mmseqs", req.model_dump())


@router.post("/fold/predict", response_model=JobCreated)
async def fold_predict(req: FoldRequest) -> JobCreated:
    """蛋白质结构预测（ESMFold）。默认走远程。"""
    return _submit("fold", req.model_dump())
