"""DiffDock 分子对接。

上游 https://github.com/gcorso/DiffDock （MIT）。
本地走子进程调用仓库自带的 inference.py，避免把它那套 torch-geometric 依赖
和本服务的进程混在一起。
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

from app.config import settings
from app.engines.base import Engine, EngineNotReady, Provider
from app.jobs import JobContext
from app.nvidia_api import call_nim


def _resolve_upload(file_id: str) -> Path:
    path = settings.uploads_dir / file_id
    if not path.is_file():
        raise EngineNotReady(f"上传文件不存在: {file_id}")
    return path


class DiffDockLocal(Provider):
    kind = "local"
    required_modules = ("torch", "torch_geometric", "rdkit")
    note = (
        "子进程调用上游 inference.py。需先跑 scripts/setup-diffdock.sh 拉源码，"
        "并 uv sync --group diffdock。代码已写好但尚未实测。"
    )

    def unmet(self) -> list[str]:
        problems = super().unmet()
        if not (settings.diffdock_repo / "inference.py").is_file():
            problems.append("缺少 DiffDock 源码（scripts/setup-diffdock.sh）")
        return problems

    def details(self) -> dict[str, Any]:
        return {
            "repo": str(settings.diffdock_repo),
            "repo_present": (settings.diffdock_repo / "inference.py").is_file(),
            "setup": "scripts/setup-diffdock.sh",
        }

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()
        protein = _resolve_upload(params["protein_file_id"])
        ligand = _resolve_upload(params["ligand_file_id"])
        out_dir = ctx.workdir / "diffdock_out"

        cmd = [
            sys.executable,
            "inference.py",
            "--protein_path",
            str(protein),
            "--ligand_description",
            str(ligand),
            "--out_dir",
            str(out_dir),
            "--samples_per_complex",
            str(params["num_poses"]),
            "--inference_steps",
            str(params["steps"]),
        ]

        ctx.progress(0.2, "启动 DiffDock 推理")
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=settings.diffdock_repo,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await proc.communicate()
        log = stdout.decode("utf-8", errors="replace")
        (ctx.workdir / "diffdock.log").write_text(log, encoding="utf-8")

        if proc.returncode != 0:
            raise RuntimeError(f"DiffDock 退出码 {proc.returncode}，详见 diffdock.log：{log[-800:]}")

        ctx.progress(0.9, "收集结果")
        return self._collect(out_dir, ctx)

    def _collect(self, out_dir: Path, ctx: JobContext) -> dict[str, Any]:
        """DiffDock 输出形如 rank1_confidence-0.61.sdf，从文件名里解析置信度。"""
        poses = []
        for sdf in sorted(out_dir.rglob("rank*.sdf")):
            name = sdf.stem
            confidence = None
            if "confidence" in name:
                try:
                    confidence = float(name.split("confidence")[-1].lstrip("-_"))
                except ValueError:
                    pass
            rank = name.split("_")[0].removeprefix("rank")
            poses.append(
                {
                    "rank": int(rank) if rank.isdigit() else None,
                    "confidence": confidence,
                    "file": sdf.name,
                }
            )
            ctx.add_file(sdf)

        poses.sort(key=lambda p: p["rank"] if p["rank"] is not None else 999)
        return {"poses": poses, "num_poses": len(poses)}


class DiffDockRemote(Provider):
    kind = "remote"
    needs_api_key = True
    note = "调用 build.nvidia.com 托管的 DiffDock NIM，不需要本地显卡"

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()
        protein = _resolve_upload(params["protein_file_id"])
        ligand = _resolve_upload(params["ligand_file_id"])

        ctx.progress(0.3, "调用远程 API")
        # 字段名对齐官方 /molecular-docking/diffdock/generate 接口
        payload = {
            "protein": protein.read_text(encoding="utf-8", errors="replace"),
            "ligand": ligand.read_text(encoding="utf-8", errors="replace"),
            "ligand_file_type": ligand.suffix.lstrip(".").lower() or "sdf",
            "num_poses": params["num_poses"],
            "time_divisions": params["time_divisions"],
            "steps": params["steps"],
            "save_trajectory": params["save_trajectory"],
            "is_staged": False,
        }
        data = await call_nim("/mit/diffdock", payload)

        if data.get("status") not in (None, "success"):
            raise RuntimeError(f"远程对接失败：{str(data)[:300]}")

        ctx.progress(0.8, "写出构象")
        positions = data.get("ligand_positions") or []
        confidences = data.get("position_confidence") or []

        poses = []
        for i, sdf_text in enumerate(positions):
            conf = confidences[i] if i < len(confidences) else None
            fname = f"rank{i + 1}.sdf"
            path = ctx.workdir / fname
            path.write_text(sdf_text, encoding="utf-8")
            ctx.add_file(path)
            poses.append({"rank": i + 1, "confidence": conf, "file": fname})

        # 蛋白也存一份，前端 Mol* 要蛋白+配体同屏
        protein_out = ctx.workdir / "protein.pdb"
        protein_out.write_text(payload["protein"], encoding="utf-8")
        ctx.add_file(protein_out)

        return {
            "poses": poses,
            "num_poses": len(poses),
            "protein_file": protein_out.name,
        }


diffdock_engine = Engine("diffdock", local=DiffDockLocal(), remote=DiffDockRemote())
