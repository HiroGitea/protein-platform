"""API 出入参定义。前端按这些字段对接。"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class JobFile(BaseModel):
    name: str
    size: int
    url: str


class Job(BaseModel):
    id: str
    engine: str
    status: JobStatus
    progress: float = Field(0.0, ge=0.0, le=1.0)
    message: str = ""
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    params: dict[str, Any] = {}
    result: dict[str, Any] | None = None
    files: list[JobFile] = []
    error: str | None = None

    @property
    def duration_seconds(self) -> float | None:
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


class JobCreated(BaseModel):
    job_id: str
    status: JobStatus


class EngineStatus(BaseModel):
    name: str
    available: bool
    reason: str = ""
    checkpoint_present: bool = False
    details: dict[str, Any] = {}


class GpuInfo(BaseModel):
    available: bool
    name: str | None = None
    driver_version: str | None = None
    memory_total_mb: int | None = None
    memory_used_mb: int | None = None
    compute_capability: str | None = None
    torch_version: str | None = None
    reason: str = ""


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    gpu: GpuInfo
    engines: list[EngineStatus]


# ---- 各引擎的请求体 ----


class GenMolRequest(BaseModel):
    mode: Literal["denovo", "fragment_completion", "fragment_linking"] = "denovo"
    smiles: str | None = Field(None, description="片段模式下的输入 SMILES，支持 * 连接点")
    num_samples: int = Field(10, ge=1, le=1000)
    softmax_temp: float = Field(1.0, gt=0, le=5)
    randomness: float = Field(0.3, ge=0, le=5)
    min_add_len: int = Field(60, ge=1, le=256)


class DiffDockRequest(BaseModel):
    protein_file_id: str
    ligand_file_id: str
    num_poses: int = Field(10, ge=1, le=40)
    inference_steps: int = Field(20, ge=1, le=100)


class MMseqsRequest(BaseModel):
    sequence: str | None = None
    file_id: str | None = None
    database: str = "swissprot"
    sensitivity: float = Field(5.7, ge=1.0, le=7.5)
    max_hits: int = Field(50, ge=1, le=1000)


class FoldRequest(BaseModel):
    sequence: str
    model: Literal["esmfold", "colabfold"] = "esmfold"


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
