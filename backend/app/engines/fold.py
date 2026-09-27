"""蛋白质结构预测（ESMFold）。

不用完整 AlphaFold2/OpenFold：MSA 数据库 2TB 起步，单卡场景不现实。
ESMFold 不需要 MSA，单序列直接出结构，16GB 显存能覆盖中等长度序列。
"""

from __future__ import annotations

from typing import Any

from app.engines.base import Engine, Provider
from app.jobs import JobContext
from app.nvidia_api import call_nim


class EsmFoldLocal(Provider):
    kind = "local"
    implemented = False
    required_modules = ("torch", "transformers")
    note = (
        "接口预留。实现方式：transformers 的 EsmForProteinFolding "
        "（facebook/esmfold_v1，权重约 2.6GB，首次运行自动下载）。"
        "长序列显存吃紧时用 model.trunk.set_chunk_size(64) 分块。"
    )

    def __init__(self) -> None:
        self._model: Any = None

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()  # implemented=False，这里必定抛出
        raise AssertionError("unreachable")

    # 实现时把下面这段接到 run 里即可：
    #
    # def _fold(self, sequence: str) -> str:
    #     import torch
    #     from transformers import AutoTokenizer, EsmForProteinFolding
    #     if self._model is None:
    #         self._tok = AutoTokenizer.from_pretrained("facebook/esmfold_v1")
    #         self._model = EsmForProteinFolding.from_pretrained("facebook/esmfold_v1")
    #         self._model = self._model.to(settings.device).eval()
    #     inputs = self._tok([sequence], return_tensors="pt", add_special_tokens=False)
    #     inputs = {k: v.to(settings.device) for k, v in inputs.items()}
    #     with torch.no_grad():
    #         output = self._model(**inputs)
    #     return self._model.output_to_pdb(output)[0]


class EsmFoldRemote(Provider):
    kind = "remote"
    needs_api_key = True
    note = "调用 build.nvidia.com 托管的 ESMFold NIM，不需要本地显卡"

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()
        sequence = params["sequence"].strip().upper()

        ctx.progress(0.3, "调用远程 API")
        data = await call_nim("/nvidia/esmfold", {"sequence": sequence})

        ctx.progress(0.8, "写出 PDB")
        pdbs = data.get("pdbs") or []
        if not pdbs:
            raise RuntimeError(f"远程未返回结构：{str(data)[:300]}")

        out = ctx.workdir / "predicted.pdb"
        out.write_text(pdbs[0], encoding="utf-8")
        ctx.add_file(out)

        return {
            "sequence_length": len(sequence),
            "pdb_file": out.name,
            # 前端 Mol* 直接用这个 URL 加载结构
            "viewer_url": f"/api/jobs/{ctx.job.id}/files/{out.name}",
        }


fold_engine = Engine("fold", local=EsmFoldLocal(), remote=EsmFoldRemote())
