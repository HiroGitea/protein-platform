"""引擎与 provider 抽象。

一个引擎 = 一个功能（分子生成、对接……），下面挂两个 provider：

- local  : 跑在本机 GPU / 本机二进制上
- remote : 调官方托管 API

两者实现同一个接口，前端感知不到区别。缺依赖、缺权重、缺 API key 时，
provider 如实报告"不可用 + 原因"，绝不返回假数据。
"""

from __future__ import annotations

import importlib.util
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Literal

from app.config import settings
from app.jobs import JobContext
from app.schemas import EngineStatus, ProviderStatus

ProviderKind = Literal["local", "remote"]


class EngineNotReady(RuntimeError):
    """provider 不具备运行条件。会被任务层捕获，变成任务失败信息回传前端。"""


def module_installed(name: str) -> bool:
    """只查包在不在，不真正 import（避免把 torch 拉进内存）。"""
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


class Provider(ABC):
    kind: ClassVar[ProviderKind]

    #: 运行所需的 python 包
    required_modules: ClassVar[tuple[str, ...]] = ()
    #: 需要的权重文件名（相对 checkpoint_dir）
    checkpoint_name: ClassVar[str | None] = None
    #: 是否需要 NVIDIA API key
    needs_api_key: ClassVar[bool] = False
    #: 代码是否已实现。False 表示接口预留但还没写实现
    implemented: ClassVar[bool] = True
    #: 补充说明，会原样回给前端（比如"计划怎么做"）
    note: ClassVar[str] = ""

    def unmet(self) -> list[str]:
        """列出所有不满足的条件。空列表 = 可用。"""
        problems: list[str] = []

        if not self.implemented:
            problems.append("尚未实现")

        missing = [m for m in self.required_modules if not module_installed(m)]
        if missing:
            problems.append(f"缺少依赖 {', '.join(missing)}")

        if self.checkpoint_name and not (settings.checkpoint_dir / self.checkpoint_name).exists():
            problems.append(f"缺少权重 checkpoints/{self.checkpoint_name}")

        if self.needs_api_key and not settings.nvidia_api_key:
            problems.append("未配置 NVIDIA_API_KEY")

        return problems

    def status(self) -> ProviderStatus:
        problems = self.unmet()
        return ProviderStatus(
            kind=self.kind,
            available=not problems,
            reason="；".join(problems),
            note=self.note,
            details=self.details(),
        )

    def details(self) -> dict[str, Any]:
        return {}

    def ensure_ready(self) -> None:
        problems = self.unmet()
        if problems:
            raise EngineNotReady("；".join(problems))

    @abstractmethod
    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        """真正干活。由 JobManager 在后台任务里调用。"""


class Engine:
    """把同一功能的 local / remote 两个 provider 包在一起。"""

    def __init__(
        self,
        name: str,
        *,
        local: Provider | None = None,
        remote: Provider | None = None,
    ) -> None:
        self.name = name
        self.local = local
        self.remote = remote

    @property
    def preference(self) -> str:
        """从配置读该引擎的 provider 偏好：auto / local / remote。"""
        return settings.provider_preference(self.name)

    def pick(self) -> Provider:
        """按偏好选一个能用的 provider，都不能用就抛错说明原因。"""
        pref = self.preference
        candidates: list[Provider]
        if pref == "local":
            candidates = [p for p in (self.local,) if p]
        elif pref == "remote":
            candidates = [p for p in (self.remote,) if p]
        else:  # auto：本地优先，不行再退远程
            candidates = [p for p in (self.local, self.remote) if p]

        if not candidates:
            raise EngineNotReady(f"{self.name} 没有配置 {pref} provider")

        for provider in candidates:
            if not provider.unmet():
                return provider

        detail = "；".join(f"{p.kind}: {'、'.join(p.unmet())}" for p in candidates)
        raise EngineNotReady(f"{self.name} 无可用 provider（{detail}）")

    def status(self) -> EngineStatus:
        providers = [p.status() for p in (self.local, self.remote) if p]
        try:
            active: str | None = self.pick().kind
        except EngineNotReady:
            active = None
        return EngineStatus(
            name=self.name,
            available=active is not None,
            preference=self.preference,
            active=active,
            providers=providers,
            reason="" if active else "；".join(f"{p.kind}({p.reason})" for p in providers if p.reason),
        )

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        provider = self.pick()
        ctx.job.message = f"使用 {provider.kind} provider"
        result = await provider.run(params, ctx)
        result.setdefault("provider", provider.kind)
        return result
