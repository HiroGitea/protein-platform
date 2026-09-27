"""引擎抽象。

设计原则：**重型依赖一律延迟导入**。
服务启动时不 import torch，只做静态检查（包在不在、权重在不在），
这样没装 GPU 依赖时 API 仍然能起来，前端能拿到"未就绪 + 原因"而不是连接被拒。
"""

from __future__ import annotations

import importlib.util
from abc import ABC, abstractmethod
from typing import Any

from app.config import settings
from app.jobs import JobContext
from app.schemas import EngineStatus


class EngineNotReady(RuntimeError):
    """引擎依赖或权重缺失。会被任务层捕获，变成任务失败信息回传前端。"""


def module_installed(name: str) -> bool:
    """只查包在不在，不真正 import（避免把 torch 拉进内存）。"""
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


class Engine(ABC):
    name: str
    #: 运行所需的 python 包
    required_modules: tuple[str, ...] = ()
    #: 需要的权重文件名（相对 checkpoint_dir），空表示不需要
    checkpoint_name: str | None = None

    def checkpoint_path(self):
        if not self.checkpoint_name:
            return None
        return settings.checkpoint_dir / self.checkpoint_name

    def missing_modules(self) -> list[str]:
        return [m for m in self.required_modules if not module_installed(m)]

    def checkpoint_present(self) -> bool:
        path = self.checkpoint_path()
        return path is None or path.exists()

    def status(self) -> EngineStatus:
        missing = self.missing_modules()
        ckpt_ok = self.checkpoint_present()
        reasons = []
        if missing:
            reasons.append(f"缺少依赖: {', '.join(missing)}（uv sync --group {self.name}）")
        if not ckpt_ok:
            reasons.append(f"缺少权重: checkpoints/{self.checkpoint_name}")
        return EngineStatus(
            name=self.name,
            available=not missing and ckpt_ok,
            reason=" / ".join(reasons),
            checkpoint_present=ckpt_ok,
            details=self.extra_details(),
        )

    def extra_details(self) -> dict[str, Any]:
        return {}

    def ensure_ready(self) -> None:
        status = self.status()
        if not status.available:
            raise EngineNotReady(f"{self.name} 未就绪：{status.reason}")

    @abstractmethod
    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        """真正干活。由 JobManager 在后台任务里调用。"""
