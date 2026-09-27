"""DiffDock 分子对接引擎（待实现）。"""

from __future__ import annotations

from app.engines._planned import PlannedEngine


class DiffDockEngine(PlannedEngine):
    name = "diffdock"
    required_modules = ("torch", "torch_geometric", "rdkit")
    plan = (
        "计划用 DiffDock-L：clone 上游仓库、装 torch-geometric（注意要用 cu128 构建以支持 sm_120）、"
        "下载 ESM2 embedding 与模型权重，输入 PDB+SDF/SMILES，输出 rank*.sdf 与 confidence。"
        "16GB 显存足够。"
    )
