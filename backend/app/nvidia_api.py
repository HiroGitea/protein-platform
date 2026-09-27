"""NVIDIA NIM 托管 API 的共享客户端。

免费 API key 在 https://build.nvidia.com 注册后获取，填到 .env 的 NVIDIA_API_KEY。

各模型的 endpoint 与请求体：
- MolMIM   /nvidia/molmim/generate   官方 schema 已核实
- DiffDock /mit/diffdock             官方 schema 已核实
- GenMol   /nvidia/genmol/generate   字段名未逐一核实，以官方文档为准
- ESMFold  /nvidia/esmfold           字段名未逐一核实，以官方文档为准

标注"未核实"的部分如果调用报 422，对照
https://docs.api.nvidia.com/nim/reference/ 调整字段名即可，改这一个文件就够。
"""

from __future__ import annotations

from typing import Any

import httpx

from app.config import settings


class RemoteApiError(RuntimeError):
    """远程 API 调用失败。"""


async def call_nim(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST 到 NIM 的某个 endpoint，返回解析后的 JSON。

    Args:
        path: 相对 nvidia_api_base 的路径，如 "/nvidia/molmim/generate"
        payload: 请求体
    """
    if not settings.nvidia_api_key:
        raise RemoteApiError("未配置 NVIDIA_API_KEY，去 https://build.nvidia.com 申请后填入 .env")

    url = f"{settings.nvidia_api_base}{path}"
    headers = {
        "Authorization": f"Bearer {settings.nvidia_api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=settings.remote_timeout_seconds) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
        except httpx.RequestError as exc:
            raise RemoteApiError(f"无法连接 {url}：{exc}") from exc

    if resp.status_code == 401:
        raise RemoteApiError("NVIDIA_API_KEY 无效或已过期")
    if resp.status_code == 422:
        raise RemoteApiError(f"请求体不被接受（字段名可能有变动）：{resp.text[:500]}")
    if resp.status_code >= 400:
        raise RemoteApiError(f"{resp.status_code} {resp.text[:500]}")

    try:
        return resp.json()
    except ValueError as exc:
        raise RemoteApiError(f"响应不是合法 JSON：{resp.text[:200]}") from exc
