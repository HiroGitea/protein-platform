"""MMseqs2 序列搜索。

MMseqs2 是 CPU 工具（GPU 模式要求整个库塞进显存，16GB 不现实），
通过子进程调用命令行二进制，不链接其代码——这一点对许可证很重要：
MMseqs2 是 GPLv3，子进程调用不影响本项目的 Apache-2.0。

只有 local provider：官方没有对等的托管搜索 API。
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path
from typing import Any

from app.config import settings
from app.engines.base import Engine, EngineNotReady, Provider
from app.jobs import JobContext

#: convertalis 的输出列，顺序必须和下面的解析一致
BLAST_TAB_COLUMNS = [
    "query",
    "target",
    "fident",
    "alnlen",
    "mismatch",
    "gapopen",
    "qstart",
    "qend",
    "tstart",
    "tend",
    "evalue",
    "bits",
]


class MMseqsLocal(Provider):
    kind = "local"
    note = (
        "需要 mmseqs 二进制（scripts/setup-mmseqs.sh）和已建好的数据库"
        "（scripts/build-mmseqs-db.sh）。SwissProt 几百 MB，UniRef50 几十 GB。"
        "代码已写好但尚未实测。"
    )

    def unmet(self) -> list[str]:
        problems = super().unmet()
        if not shutil.which(settings.mmseqs_binary):
            problems.append(f"找不到 {settings.mmseqs_binary} 二进制")
        if not self.available_databases():
            problems.append(f"没有已建好的数据库（{settings.database_dir}）")
        return problems

    def available_databases(self) -> list[str]:
        """建好的库会在 database_dir 下留一个同名的 .dbtype 文件。"""
        if not settings.database_dir.is_dir():
            return []
        return sorted(p.stem for p in settings.database_dir.glob("*.dbtype") if "_" not in p.stem)

    def details(self) -> dict[str, Any]:
        return {
            "binary": shutil.which(settings.mmseqs_binary) or "未安装",
            "runs_on": "CPU",
            "databases": self.available_databases(),
            "setup": "scripts/setup-mmseqs.sh",
        }

    async def _run_cmd(self, *args: str, ctx: JobContext) -> None:
        proc = await asyncio.create_subprocess_exec(
            settings.mmseqs_binary,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await proc.communicate()
        log = stdout.decode("utf-8", errors="replace")
        with (ctx.workdir / "mmseqs.log").open("a", encoding="utf-8") as fh:
            fh.write(f"$ mmseqs {' '.join(args)}\n{log}\n")
        if proc.returncode != 0:
            raise RuntimeError(f"mmseqs {args[0]} 失败（退出码 {proc.returncode}）：{log[-800:]}")

    def _write_query(self, params: dict[str, Any], workdir: Path) -> Path:
        """把序列或上传的文件写成 FASTA。"""
        query = workdir / "query.fasta"
        if params.get("file_id"):
            src = settings.uploads_dir / params["file_id"]
            if not src.is_file():
                raise EngineNotReady(f"上传文件不存在: {params['file_id']}")
            query.write_text(src.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        elif params.get("sequence"):
            seq = params["sequence"].strip()
            if not seq.startswith(">"):
                seq = f">query\n{seq}"
            query.write_text(seq + "\n", encoding="utf-8")
        else:
            raise ValueError("必须提供 sequence 或 file_id")
        return query

    async def run(self, params: dict[str, Any], ctx: JobContext) -> dict[str, Any]:
        self.ensure_ready()

        database = params["database"]
        if database not in self.available_databases():
            raise EngineNotReady(f"数据库 {database} 未建，现有：{self.available_databases() or '无'}")

        wd = ctx.workdir
        query_fasta = self._write_query(params, wd)
        query_db, result_db, tmp = wd / "queryDB", wd / "resultDB", wd / "tmp"
        target_db = settings.database_dir / database
        hits_tsv = wd / "hits.tsv"

        ctx.progress(0.2, "建立查询库")
        await self._run_cmd("createdb", str(query_fasta), str(query_db), ctx=ctx)

        ctx.progress(0.4, "搜索中")
        await self._run_cmd(
            "search",
            str(query_db),
            str(target_db),
            str(result_db),
            str(tmp),
            "-s",
            str(params["sensitivity"]),
            "--max-seqs",
            str(params["max_hits"]),
            ctx=ctx,
        )

        ctx.progress(0.8, "导出结果")
        await self._run_cmd(
            "convertalis",
            str(query_db),
            str(target_db),
            str(result_db),
            str(hits_tsv),
            "--format-output",
            ",".join(BLAST_TAB_COLUMNS),
            ctx=ctx,
        )
        ctx.add_file(hits_tsv)

        return {"database": database, "hits": self._parse_hits(hits_tsv, params["max_hits"])}

    def _parse_hits(self, tsv: Path, limit: int) -> list[dict[str, Any]]:
        hits: list[dict[str, Any]] = []
        if not tsv.is_file():
            return hits
        for line in tsv.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) != len(BLAST_TAB_COLUMNS):
                continue
            row = dict(zip(BLAST_TAB_COLUMNS, parts, strict=True))
            hits.append(
                {
                    "target": row["target"],
                    "identity": round(float(row["fident"]) * 100, 2),
                    "alignment_length": int(row["alnlen"]),
                    "evalue": row["evalue"],
                    "bit_score": float(row["bits"]),
                }
            )
            if len(hits) >= limit:
                break
        return hits


mmseqs_engine = Engine("mmseqs", local=MMseqsLocal())
