from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.jobs import job_manager
from app.schemas import Job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[Job])
def list_jobs(engine: str | None = None, limit: int = 50) -> list[Job]:
    return job_manager.list(engine=engine, limit=limit)


@router.get("/{job_id}", response_model=Job)
def get_job(job_id: str) -> Job:
    job = job_manager.get(job_id)
    if job is None:
        raise HTTPException(404, f"任务不存在: {job_id}")
    return job


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str) -> dict[str, bool]:
    return {"cancelled": job_manager.cancel(job_id)}


@router.get("/{job_id}/files/{filename}")
def download(job_id: str, filename: str) -> FileResponse:
    # 防目录穿越：只允许取该任务目录下的直接子文件
    workdir = (settings.jobs_dir / job_id).resolve()
    path = (workdir / filename).resolve()
    if workdir.parent != settings.jobs_dir.resolve() or path.parent != workdir or not path.is_file():
        raise HTTPException(404, "文件不存在")
    return FileResponse(path, filename=filename)
