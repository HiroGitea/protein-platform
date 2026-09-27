"""GenMol 分子生成。

上游 https://github.com/NVIDIA-Digital-Bio/genmol
89M 参数的 masked discrete diffusion，代码 Apache-2.0、权重 NVIDIA Open Model License。
"""

from __future__ import annotations

import asyncio
import functools
import sys
from typing import Any

from app.chem import score_smiles, summarize
from app.config import settings
from app.engines.base import Engine, EngineNotReady, Provider
from app.jobs import JobContext
from app.nvidia_api import call_nim


class GenMolLocal(Provider):
    kind = "local"
    required_modules = ("torch", "transformers", "lightning", "safe", "rdkit")
    checkpoint_name = settings.genmol_checkpoint
    note = "89M 参数，显存占用很小；需 torch>=2.7 才支持 Blackwell(sm_120)"

    def __init__(self) -> None:
        self._sampler: Any = None

    def details(self) -> dict[str, Any]:
        return {
            "repo": str(settings.genmol_repo),
            "repo_present": (settings.genmol_repo / "src" / "genmol").is_dir(),
            "setup": "scripts/setup-genmol.sh",
        }

    def _load_sampler(self):
        """首次调用时加载模型并常驻显存，后续请求复用。"""
        if self._sampler is not None:
            return self._sampler

        repo_src = settings.genmol_repo / "src"
        if not (repo_src / "genmol").is_dir():
            raise EngineNotReady(f"genmol 源码不在 {repo_src}，先跑 scripts/setup-genmol.sh")
        if str(repo_src) not in sys.path:
            sys.path.insert(0, str(repo_src))

        from genmol.sampler import Sampler

        self._sampler = Sampler(str(settings.checkpoint_dir / self.checkpoint_name))
        return self._sampler

    def _generate(self, params: dict[str, Any]) -> list[str]:
        sampler = self._load_sampler()
        mode = params.get("mode", "denovo")
        n = params["num_samples"]
        kw = {"softmax_temp": params["softmax_temp"], "randomness": params["randomness"]}

        if mode == "denovo":
            return sampler.de_novo_generation(n, min_add_len=params["min_add_len"], **kw)

        smiles = params.get("smiles")
        if not smiles:
            raise ValueError(f"{mode} 模式必须提供 smiles")
        if mode == "fragment_completion":
            return sampler.fragment_completion(smiles, num_samples=n, **kw)
        if mode == "fragment_linking":
            return sampler.fragment_linking(smiles, num_samples=n, **kw)
        raise ValueError(f"未知模式: {mode}")

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()
        loop = asyncio.get_running_loop()

        ctx.progress(0.1, "加载模型")
        await loop.run_in_executor(None, self._load_sampler)

        ctx.progress(0.3, "生成分子")
        smiles = await loop.run_in_executor(None, functools.partial(self._generate, params))

        ctx.progress(0.8, "计算性质")
        rows = await loop.run_in_executor(None, functools.partial(score_smiles, smiles))

        out = ctx.workdir / "molecules.smi"
        out.write_text("\n".join(r["smiles"] for r in rows), encoding="utf-8")
        ctx.add_file(out)
        return summarize(rows, params["num_samples"])


class GenMolRemote(Provider):
    kind = "remote"
    needs_api_key = True
    note = "调用 build.nvidia.com 托管的 GenMol NIM，不需要本地显卡"

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()
        ctx.progress(0.3, "调用远程 API")

        # 远程只支持带起始片段的生成，de novo 用通配片段起头
        payload = {
            "smiles": params.get("smiles") or "C1=CC=CC=C1",
            "num_molecules": params["num_samples"],
            "temperature": params["softmax_temp"],
            "noise": params["randomness"],
            "step_size": 1,
            "scoring": "QED",
        }
        data = await call_nim("/nvidia/genmol/generate", payload)

        ctx.progress(0.8, "解析结果")
        molecules = data.get("molecules", [])
        # 响应可能是 [{"smiles":..,"score":..}] 或直接是字符串数组，两种都兼容
        smiles = [m["smiles"] if isinstance(m, dict) else m for m in molecules]
        rows = score_smiles(smiles)

        out = ctx.workdir / "molecules.smi"
        out.write_text("\n".join(r["smiles"] for r in rows), encoding="utf-8")
        ctx.add_file(out)
        return summarize(rows, params["num_samples"])


genmol_engine = Engine("genmol", local=GenMolLocal(), remote=GenMolRemote())
