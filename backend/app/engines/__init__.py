"""引擎注册表。每个引擎自己声明就绪状态，缺依赖不会拖垮整个服务。"""

from __future__ import annotations

from app.engines.base import Engine, EngineNotReady, Provider
from app.engines.diffdock import diffdock_engine
from app.engines.fold import fold_engine
from app.engines.genmol import genmol_engine
from app.engines.mmseqs import mmseqs_engine
from app.engines.molmim import molmim_engine

ENGINES: dict[str, Engine] = {
    e.name: e for e in (genmol_engine, molmim_engine, diffdock_engine, mmseqs_engine, fold_engine)
}

__all__ = ["ENGINES", "Engine", "EngineNotReady", "Provider"]
