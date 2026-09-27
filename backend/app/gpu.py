"""GPU 状态探测。torch 没装时退回 nvidia-smi，保证框架阶段也能看到显卡信息。"""

from __future__ import annotations

import shutil
import subprocess

from app.schemas import GpuInfo


def _from_nvidia_smi() -> GpuInfo:
    exe = shutil.which("nvidia-smi")
    if not exe:
        return GpuInfo(available=False, reason="未找到 nvidia-smi")
    try:
        out = (
            subprocess.run(
                [
                    exe,
                    "--query-gpu=name,driver_version,memory.total,memory.used,compute_cap",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            .stdout.strip()
            .splitlines()[0]
        )
    except (subprocess.SubprocessError, IndexError) as exc:
        return GpuInfo(available=False, reason=f"nvidia-smi 调用失败: {exc}")

    name, driver, total, used, cap = [p.strip() for p in out.split(",")]
    return GpuInfo(
        available=True,
        name=name,
        driver_version=driver,
        memory_total_mb=int(float(total)),
        memory_used_mb=int(float(used)),
        compute_capability=cap,
        reason="torch 未安装，信息来自 nvidia-smi",
    )


def get_gpu_info() -> GpuInfo:
    try:
        import torch
    except ImportError:
        return _from_nvidia_smi()

    if not torch.cuda.is_available():
        info = _from_nvidia_smi()
        info.available = False
        info.torch_version = torch.__version__
        info.reason = "torch 已安装但 torch.cuda.is_available() 为 False（多半是装成了 CPU 版）"
        return info

    props = torch.cuda.get_device_properties(0)
    free, total = torch.cuda.mem_get_info(0)
    cap = f"{props.major}.{props.minor}"

    reason = ""
    # sm_120 = Blackwell。torch < 2.7 的 wheel 里没有对应 kernel，跑起来会报
    # "no kernel image is available for execution on the device"
    if props.major >= 12 and torch.__version__ < "2.7":
        reason = f"⚠️ 检测到 sm_{props.major}{props.minor} 但 torch=={torch.__version__}，需要 >=2.7 才有对应 kernel"

    return GpuInfo(
        available=True,
        name=props.name,
        memory_total_mb=total // (1024 * 1024),
        memory_used_mb=(total - free) // (1024 * 1024),
        compute_capability=cap,
        torch_version=torch.__version__,
        reason=reason,
    )
