"""MolMIM 分子优化。

70M 参数的受控生成模型，用 CMA-ES 在潜空间里搜索满足性质约束的分子。

本地路径故意留空：MolMIM 的权重是 .nemo 格式，要拖进整套 NeMo + Megatron +
BioNeMo Framework 才能跑，容器几十 GB 且与 CUDA 版本强绑定——为一个 70M 的模型
付这个代价不划算，Blackwell 上还容易翻车。所以默认走远程，接口保留。
"""

from __future__ import annotations

from typing import Any

from app.chem import score_smiles, summarize
from app.engines.base import Engine, Provider
from app.jobs import JobContext
from app.nvidia_api import call_nim


class MolMimLocal(Provider):
    kind = "local"
    implemented = False
    required_modules = ("torch", "bionemo")
    checkpoint_name = "molmim_70m_24_3.nemo"
    note = (
        "接口预留。要跑本地版需要 BioNeMo Framework + NeMo + Megatron，"
        "权重从 NGC 获取（NVIDIA AI Foundation Models Community License）。"
        "对展示用途来说远程 provider 已经够用。"
    )

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()  # implemented=False，这里必定抛出
        raise AssertionError("unreachable")


class MolMimRemote(Provider):
    kind = "remote"
    needs_api_key = True
    note = "调用 build.nvidia.com 托管的 MolMIM NIM"

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()
        ctx.progress(0.3, "调用远程 API")

        # 字段名对齐官方 /generate 接口
        payload = {
            "smi": params["smiles"],
            "algorithm": params["algorithm"],
            "num_molecules": params["num_molecules"],
            "property_name": params["property_name"],
            "minimize": params["minimize"],
            "iterations": params["iterations"],
            "particles": params["particles"],
            "min_similarity": params["min_similarity"],
            "scaled_radius": params["scaled_radius"],
        }
        data = await call_nim("/nvidia/molmim/generate", payload)

        ctx.progress(0.8, "解析结果")
        generated = data.get("generated", [])
        # 官方返回 {"generated": [...]}，个别版本会把它序列化成 JSON 字符串
        if isinstance(generated, str):
            import json

            generated = json.loads(generated)
        smiles = [g["smiles"] if isinstance(g, dict) else g for g in generated]
        rows = score_smiles(smiles)

        out = ctx.workdir / "optimized.smi"
        out.write_text("\n".join(r["smiles"] for r in rows), encoding="utf-8")
        ctx.add_file(out)

        result = summarize(rows, params["num_molecules"])
        result["input_smiles"] = params["smiles"]
        result["optimized_property"] = params["property_name"]
        if rows:
            best = max(rows, key=lambda r: r.get("qed", 0))
            result["best"] = best
        return result


molmim_engine = Engine("molmim", local=MolMimLocal(), remote=MolMimRemote())
