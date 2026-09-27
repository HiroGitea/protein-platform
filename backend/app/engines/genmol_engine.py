"""GenMol 分子生成引擎。

上游：https://github.com/NVIDIA-Digital-Bio/genmol （代码 Apache-2.0，权重 NVIDIA Open Model License）
模型：89M 参数的 BERT-style masked discrete diffusion，显存占用很小，16GB 卡绰绰有余。

注意：torch / genmol 都在函数内部导入，服务启动时不加载。
"""

from __future__ import annotations

import asyncio
import functools
import sys
from typing import Any

from app.config import settings
from app.engines.base import Engine, EngineNotReady
from app.jobs import JobContext


class GenMolEngine(Engine):
    name = "genmol"
    required_modules = ("torch", "transformers", "lightning", "safe", "rdkit")
    checkpoint_name = settings.genmol_checkpoint

    def __init__(self) -> None:
        self._sampler: Any = None

    def extra_details(self) -> dict[str, Any]:
        return {
            "repo": str(settings.genmol_repo),
            "repo_present": (settings.genmol_repo / "src" / "genmol").is_dir(),
            "params": "89M",
            "license": "code Apache-2.0 / weights NVIDIA Open Model License",
        }

    def _load_sampler(self):
        """首次调用时加载模型并常驻显存，后续请求直接复用。"""
        if self._sampler is not None:
            return self._sampler

        repo_src = settings.genmol_repo / "src"
        if not (repo_src / "genmol").is_dir():
            raise EngineNotReady(f"genmol 源码不在 {repo_src}，先 git clone 上游仓库")
        if str(repo_src) not in sys.path:
            sys.path.insert(0, str(repo_src))

        from genmol.sampler import Sampler

        ckpt = self.checkpoint_path()
        self._sampler = Sampler(str(ckpt))
        return self._sampler

    def _generate_sync(self, params: dict[str, Any]) -> list[str]:
        sampler = self._load_sampler()
        mode = params.get("mode", "denovo")
        n = params["num_samples"]
        kw = {
            "softmax_temp": params["softmax_temp"],
            "randomness": params["randomness"],
        }

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

    def _score_sync(self, smiles_list: list[str]) -> list[dict[str, Any]]:
        """用 rdkit 直接算 QED/SA，不引入 PyTDC（那个包很重且容易装崩）。"""
        from rdkit import Chem
        from rdkit.Chem import QED, Descriptors

        rows = []
        for smi in smiles_list:
            mol = Chem.MolFromSmiles(smi)
            if mol is None:
                continue
            rows.append(
                {
                    "smiles": smi,
                    "qed": round(QED.qed(mol), 4),
                    "mol_weight": round(Descriptors.MolWt(mol), 2),
                    "logp": round(Descriptors.MolLogP(mol), 3),
                    "num_atoms": mol.GetNumHeavyAtoms(),
                }
            )
        return rows

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()
        loop = asyncio.get_running_loop()

        ctx.progress(0.1, "加载模型")
        await loop.run_in_executor(None, self._load_sampler)

        ctx.progress(0.3, "生成分子")
        smiles_list = await loop.run_in_executor(None, functools.partial(self._generate_sync, params))

        ctx.progress(0.8, "计算性质")
        rows = await loop.run_in_executor(None, functools.partial(self._score_sync, smiles_list))

        out = ctx.workdir / "molecules.smi"
        out.write_text("\n".join(r["smiles"] for r in rows), encoding="utf-8")
        ctx.add_file(out)

        requested = params["num_samples"]
        return {
            "molecules": rows,
            "requested": requested,
            "generated": len(smiles_list),
            "valid": len(rows),
            "validity": round(len(rows) / requested, 4) if requested else 0.0,
            "unique": len({r["smiles"] for r in rows}),
        }
