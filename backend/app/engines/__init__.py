"""引擎注册表。每个引擎自己声明是否就绪，没装依赖不会拖垮整个服务。"""

from __future__ import annotations

from app.engines.base import Engine
from app.engines.diffdock_engine import DiffDockEngine
from app.engines.fold_engine import FoldEngine
from app.engines.genmol_engine import GenMolEngine
from app.engines.mmseqs_engine import MMseqsEngine

ENGINES: dict[str, Engine] = {
    e.name: e for e in (GenMolEngine(), DiffDockEngine(), MMseqsEngine(), FoldEngine())
}

__all__ = ["ENGINES", "Engine"]
