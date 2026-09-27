"""全局配置：路径、权重位置、provider 偏好、API key。

环境变量前缀 PROTEIN_，另外单独读 NVIDIA_API_KEY（沿用官方惯例）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

ProviderPreference = Literal["auto", "local", "remote"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PROTEIN_", env_file=".env", extra="ignore")

    # ---- 存储 ----
    storage_dir: Path = BASE_DIR / "storage"
    checkpoint_dir: Path = BASE_DIR / "checkpoints"
    database_dir: Path = BASE_DIR / "databases"

    # ---- 第三方源码（由 scripts/setup-*.sh 克隆）----
    genmol_repo: Path = BASE_DIR / "genmol"
    diffdock_repo: Path = BASE_DIR / "third_party" / "DiffDock"

    # ---- 权重文件名（放在 checkpoint_dir 下）----
    genmol_checkpoint: str = "model_v2.ckpt"

    # ---- 外部二进制 ----
    mmseqs_binary: str = "mmseqs"

    # ---- provider 偏好：auto 本地优先、不行退远程 ----
    genmol_provider: ProviderPreference = "auto"
    molmim_provider: ProviderPreference = "auto"
    diffdock_provider: ProviderPreference = "auto"
    fold_provider: ProviderPreference = "auto"
    mmseqs_provider: ProviderPreference = "auto"

    # ---- 远程 API ----
    # 注意：这个不带 PROTEIN_ 前缀，直接叫 NVIDIA_API_KEY
    nvidia_api_key: str = Field("", validation_alias="NVIDIA_API_KEY")
    nvidia_api_base: str = "https://health.api.nvidia.com/v1/biology"
    remote_timeout_seconds: float = 300.0

    # ---- AlphaFold 2 NIM（独立服务，不复用 biology API 路径或凭据）----
    af2_local_url: str = ""
    af2_remote_url: str = ""
    af2_api_key: str = ""
    af2_timeout_seconds: float = Field(7200.0, gt=0)
    af2_poll_interval_seconds: float = Field(5.0, gt=0)

    # ---- 运行时 ----
    device: str = "cuda"
    max_concurrent_jobs: int = 1  # 单卡 16GB，默认串行，避免显存打架
    job_retention_hours: int = 24

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def uploads_dir(self) -> Path:
        return self.storage_dir / "uploads"

    @property
    def jobs_dir(self) -> Path:
        return self.storage_dir / "jobs"

    def provider_preference(self, engine: str) -> str:
        return getattr(self, f"{engine}_provider", "auto")


settings = Settings()

for _d in (settings.storage_dir, settings.uploads_dir, settings.jobs_dir, settings.checkpoint_dir):
    _d.mkdir(parents=True, exist_ok=True)
