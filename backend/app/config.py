"""全局配置：路径、模型权重位置、GPU 选择。"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PROTEIN_", env_file=".env", extra="ignore")

    # 存储
    storage_dir: Path = BASE_DIR / "storage"
    checkpoint_dir: Path = BASE_DIR / "checkpoints"

    # 上游模型源码（git clone 下来的）
    genmol_repo: Path = BASE_DIR / "genmol"
    # 权重文件名，放在 checkpoint_dir 下
    genmol_checkpoint: str = "model_v2.ckpt"

    # 运行时
    device: str = "cuda"
    max_concurrent_jobs: int = 1  # 单卡 16GB，默认串行，避免显存打架
    job_retention_hours: int = 24

    # 允许的前端来源（SvelteKit dev server）
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def uploads_dir(self) -> Path:
        return self.storage_dir / "uploads"

    @property
    def jobs_dir(self) -> Path:
        return self.storage_dir / "jobs"


settings = Settings()

for _d in (settings.storage_dir, settings.uploads_dir, settings.jobs_dir, settings.checkpoint_dir):
    _d.mkdir(parents=True, exist_ok=True)
