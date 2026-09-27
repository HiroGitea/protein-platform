"""MMseqs2 序列搜索引擎（待实现）。"""

from __future__ import annotations

from app.engines._planned import PlannedEngine


class MMseqsEngine(PlannedEngine):
    name = "mmseqs"
    required_modules = ()
    plan = (
        "MMseqs2 是 CPU 工具（GPU 模式要求整库进显存，16GB 不现实），走 subprocess 调用二进制即可。"
        "需要先安装 mmseqs2 并建库：SwissProt 约几百 MB，UniRef50 要几十 GB。"
    )

    def extra_details(self) -> dict:
        import shutil

        exe = shutil.which("mmseqs")
        return {"binary": exe or "未安装", "runs_on": "CPU"}
