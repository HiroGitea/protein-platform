"""API 出入参定义。前端按这些字段对接。"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


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


class ProviderStatus(BaseModel):
    kind: Literal["local", "remote"]
    available: bool
    reason: str = ""
    note: str = ""
    details: dict[str, Any] = {}


class EngineStatus(BaseModel):
    name: str
    available: bool
    #: 配置的偏好：auto / local / remote
    preference: str = "auto"
    #: 当前实际会用哪个 provider，None 表示都不可用
    active: str | None = None
    reason: str = ""
    providers: list[ProviderStatus] = []


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


class MolMimRequest(BaseModel):
    """字段命名对齐 NVIDIA MolMIM /generate 接口，方便远程直传。"""

    smiles: str = Field(..., description="起始分子 SMILES")
    algorithm: Literal["CMA-ES", "none"] = "CMA-ES"
    num_molecules: int = Field(10, ge=1, le=100)
    property_name: Literal["QED", "plogP"] = "QED"
    minimize: bool = False
    iterations: int = Field(10, ge=1, le=1000)
    particles: int = Field(30, ge=2, le=1000)
    min_similarity: float = Field(0.7, ge=0.0, le=0.7)
    scaled_radius: float = Field(1.0, ge=0.0, le=2.0)


class DiffDockRequest(BaseModel):
    protein_file_id: str = Field(..., description="POST /api/files 上传 PDB 后拿到的 file_id")
    ligand_file_id: str = Field(..., description="配体 SDF/MOL 的 file_id")
    num_poses: int = Field(10, ge=1, le=40)
    steps: int = Field(18, ge=1, le=100)
    time_divisions: int = Field(20, ge=1, le=100)
    save_trajectory: bool = False


class MMseqsRequest(BaseModel):
    sequence: str | None = None
    file_id: str | None = None
    database: str = "swissprot"
    sensitivity: float = Field(5.7, ge=1.0, le=7.5)
    max_hits: int = Field(50, ge=1, le=1000)


class FoldRequest(BaseModel):
    sequence: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        pattern=r"^[ARNDCQEGHILKMFPSTWYV]+$",
        description="AlphaFold 2 单条氨基酸序列（20 种标准氨基酸，不含 FASTA 标题）",
    )
    algorithm: Literal["jackhmmer", "mmseqs2"] = "jackhmmer"
    relax_prediction: bool = True

    @field_validator("sequence", mode="before")
    @classmethod
    def normalize_sequence(cls, value: Any) -> Any:
        if isinstance(value, str):
            return "".join(value.split()).upper()
        return value


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
