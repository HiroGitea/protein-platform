from __future__ import annotations

import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.schemas import UploadResponse

router = APIRouter(prefix="/files", tags=["files"])

MAX_UPLOAD_BYTES = 200 * 1024 * 1024
ALLOWED_SUFFIXES = {".pdb", ".cif", ".mmcif", ".sdf", ".mol", ".mol2", ".fasta", ".fa", ".smi", ".txt"}


@router.post("", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)) -> UploadResponse:
    name = file.filename or "unnamed"
    suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(400, f"不支持的文件类型: {suffix or '(无扩展名)'}")

    file_id = uuid.uuid4().hex[:12]
    dest = settings.uploads_dir / f"{file_id}{suffix}"

    size = 0
    with dest.open("wb") as fh:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_BYTES:
                fh.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, "文件过大（上限 200MB）")
            fh.write(chunk)

    return UploadResponse(file_id=dest.name, filename=name, size=size)
