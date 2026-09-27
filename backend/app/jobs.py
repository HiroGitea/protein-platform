"""任务管理：所有模型推理都是耗时任务，一律异步跑 + 前端轮询。

单卡 16GB，默认用信号量把并发压到 1，避免两个模型同时抢显存导致 OOM。
"""

from __future__ import annotations

import asyncio
import logging
import traceback
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from app.config import settings
from app.schemas import Job, JobFile, JobStatus

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(UTC)


class JobContext:
    """交给引擎用的上下文：报进度、拿工作目录。"""

    def __init__(self, job: Job, workdir: Path) -> None:
        self.job = job
        self.workdir = workdir

    def progress(self, value: float, message: str = "") -> None:
        self.job.progress = max(0.0, min(1.0, value))
        if message:
            self.job.message = message

    def add_file(self, path: Path) -> None:
        if not path.exists():
            return
        self.job.files.append(
            JobFile(
                name=path.name,
                size=path.stat().st_size,
                url=f"/api/jobs/{self.job.id}/files/{path.name}",
            )
        )


# 引擎签名：拿到参数和上下文，返回可序列化的结果字典
Runner = Callable[[dict[str, Any], JobContext], Awaitable[dict[str, Any]]]


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._sem = asyncio.Semaphore(settings.max_concurrent_jobs)

    def submit(self, engine: str, params: dict[str, Any], runner: Runner) -> Job:
        job_id = uuid.uuid4().hex[:12]
        job = Job(
            id=job_id,
            engine=engine,
            status=JobStatus.queued,
            created_at=_now(),
            params=params,
        )
        self._jobs[job_id] = job
        self._tasks[job_id] = asyncio.create_task(self._run(job, runner))
        return job

    async def _run(self, job: Job, runner: Runner) -> None:
        workdir = settings.jobs_dir / job.id
        workdir.mkdir(parents=True, exist_ok=True)
        ctx = JobContext(job, workdir)

        async with self._sem:
            if job.status == JobStatus.cancelled:
                return
            job.status = JobStatus.running
            job.started_at = _now()
            job.message = "运行中"
            try:
                job.result = await runner(job.params, ctx)
                job.status = JobStatus.succeeded
                job.progress = 1.0
                job.message = "完成"
            except asyncio.CancelledError:
                job.status = JobStatus.cancelled
                job.message = "已取消"
                raise
            except Exception as exc:  # noqa: BLE001 - 任何引擎异常都要变成任务失败而不是 500
                job.status = JobStatus.failed
                job.error = f"{type(exc).__name__}: {exc}"
                job.message = "失败"
                logger.error("job %s failed\n%s", job.id, traceback.format_exc())
            finally:
                job.finished_at = _now()

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def list(self, engine: str | None = None, limit: int = 50) -> list[Job]:
        jobs = sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)
        if engine:
            jobs = [j for j in jobs if j.engine == engine]
        return jobs[:limit]

    def cancel(self, job_id: str) -> bool:
        task = self._tasks.get(job_id)
        job = self._jobs.get(job_id)
        if not task or not job or job.status in (JobStatus.succeeded, JobStatus.failed):
            return False
        task.cancel()
        job.status = JobStatus.cancelled
        return True

    def purge_expired(self) -> int:
        """清掉过期任务记录（文件留在磁盘上，由运维决定是否删）。"""
        cutoff = _now() - timedelta(hours=settings.job_retention_hours)
        stale = [jid for jid, j in self._jobs.items() if j.created_at < cutoff]
        for jid in stale:
            self._jobs.pop(jid, None)
            self._tasks.pop(jid, None)
        return len(stale)


job_manager = JobManager()
