"""还没接的引擎的共同基类。

明确对外声明"未实现"，绝不返回假数据——这个后端存在的意义就是替换掉
前端里那些 setTimeout + 硬编码结果。
"""

from __future__ import annotations

from typing import Any

from app.engines.base import Engine, EngineNotReady
from app.jobs import JobContext
from app.schemas import EngineStatus


class PlannedEngine(Engine):
    #: 待办说明，会原样回给前端
    plan: str = ""

    def status(self) -> EngineStatus:
        base = super().status()
        base.available = False
        base.reason = f"引擎尚未实现。{self.plan}" if self.plan else "引擎尚未实现。"
        return base

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        raise EngineNotReady(f"{self.name} 引擎尚未实现。{self.plan}")
