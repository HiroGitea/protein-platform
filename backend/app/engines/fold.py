"""AlphaFold 2 structure prediction through a separately deployed NIM service."""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import quote

import httpx

from app.config import settings
from app.engines.base import Engine, Provider
from app.jobs import JobContext
from app.nvidia_api import RemoteApiError
from app.schemas import FoldRequest

AF2_PATH = "/protein-structure/alphafold2/predict-structure-from-sequence"


async def predict_af2(base_url: str, payload: dict[str, Any], *, api_key: str = "") -> list[str]:
    """NIM returns a JSON array of PDB strings; hosted gateways may first return 202.

    Contract: https://docs.api.nvidia.com/nim/reference/deepmind-alphafold2-infer
    Poll the configured service's status endpoint, never a response-supplied URL.
    """
    headers = {"Accept": "application/json", "NVCF-POLL-SECONDS": "30"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    base_url = base_url.rstrip("/")
    try:
        async with asyncio.timeout(settings.af2_timeout_seconds):
            async with httpx.AsyncClient(timeout=settings.af2_timeout_seconds) as client:
                response = await client.post(f"{base_url}{AF2_PATH}", json=payload, headers=headers)
                request_id = response.headers.get("nvcf-reqid")
                while response.status_code == 202:
                    if not request_id:
                        raise RemoteApiError("AlphaFold 2 returned HTTP 202 without nvcf-reqid")
                    await asyncio.sleep(settings.af2_poll_interval_seconds)
                    response = await client.get(
                        f"{base_url}/status/{quote(request_id, safe='')}", headers=headers
                    )
                if response.status_code != 200:
                    raise RemoteApiError(f"AlphaFold 2 HTTP {response.status_code}: {response.text[:500]}")
                try:
                    pdbs = response.json()
                except ValueError as exc:
                    raise RemoteApiError("AlphaFold 2 returned invalid JSON") from exc
    except (TimeoutError, httpx.TimeoutException) as exc:
        raise RemoteApiError(
            "AlphaFold 2 timed out; check the service or increase PROTEIN_AF2_TIMEOUT_SECONDS"
        ) from exc
    except httpx.RequestError as exc:
        raise RemoteApiError("Unable to connect to the configured AlphaFold 2 service") from exc

    if (
        not isinstance(pdbs, list)
        or not pdbs
        or any(
            not isinstance(pdb, str) or not any(line.startswith("ATOM  ") for line in pdb.splitlines())
            for pdb in pdbs
        )
    ):
        raise RemoteApiError("AlphaFold 2 must return a non-empty JSON array of PDB structures")
    return pdbs


class AlphaFold2Local(Provider):
    kind = "local"
    note = "AlphaFold 2 NIM 服务；需独立部署模型与数据库。健康检查仅检查地址配置。"

    @property
    def base_url(self) -> str:
        return settings.af2_local_url

    def unmet(self) -> list[str]:
        if not self.base_url:
            return ["未配置 PROTEIN_AF2_LOCAL_URL；请先部署 AlphaFold 2 NIM 服务"]
        return []

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()
        request = FoldRequest.model_validate(params)
        ctx.progress(0.1, "AlphaFold 2：生成 MSA 并预测结构")
        pdbs = await predict_af2(
            self.base_url,
            request.model_dump(),
            api_key=settings.af2_api_key if self.kind == "remote" else "",
        )
        ctx.progress(0.9, "写出 AlphaFold 2 PDB")
        filenames = []
        for index, pdb in enumerate(pdbs):
            name = "predicted.pdb" if index == 0 else f"predicted_{index + 1}.pdb"
            out = ctx.workdir / name
            out.write_text(pdb, encoding="utf-8")
            ctx.add_file(out)
            filenames.append(name)
        return {
            "model": "alphafold2",
            "sequence_length": len(request.sequence),
            "pdb_file": filenames[0],
            "pdb_files": filenames,
            "viewer_url": f"/api/jobs/{ctx.job.id}/files/{filenames[0]}",
        }


class AlphaFold2Remote(AlphaFold2Local):
    kind = "remote"
    note = "自部署的远程 AlphaFold 2 NIM。NVIDIA 公共托管端点已弃用，需显式配置服务地址。"

    @property
    def base_url(self) -> str:
        return settings.af2_remote_url

    def unmet(self) -> list[str]:
        if not self.base_url:
            return ["未配置 PROTEIN_AF2_REMOTE_URL；NVIDIA 公共 AlphaFold 2 端点已弃用"]
        return []


fold_engine = Engine("fold", local=AlphaFold2Local(), remote=AlphaFold2Remote())
