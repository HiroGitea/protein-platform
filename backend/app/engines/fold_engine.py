"""蛋白质结构预测引擎（待实现）。"""

from __future__ import annotations

from app.engines._planned import PlannedEngine


class FoldEngine(PlannedEngine):
    name = "fold"
    required_modules = ("torch", "transformers")
    plan = (
        "不建议上完整 OpenFold/AlphaFold2（MSA 数据库 2TB 起，单卡毕设不合适）。"
        "推荐 ESMFold：无需 MSA、单卡可跑；或 ColabFold 把 MSA 走远程 API。"
        "注意前端页面标题目前 OpenFold/AlphaFold 混用，接的时候统一一下。"
    )
