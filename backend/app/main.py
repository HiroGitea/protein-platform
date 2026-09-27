"""生物信息学平台后端入口。

启动：uv run uvicorn app.main:app --reload --port 8000
文档：http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.engines import ENGINES
from app.gpu import get_gpu_info
from app.routers import files, health, jobs, tools

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    gpu = get_gpu_info()
    logger.info("GPU: %s", gpu.name or "不可用")
    if gpu.reason:
        logger.warning("GPU 提示: %s", gpu.reason)
    for engine in ENGINES.values():
        st = engine.status()
        logger.info("引擎 %-9s %s %s", st.name, "就绪" if st.available else "未就绪", st.reason)
    yield


app = FastAPI(
    title="生物信息学平台 API",
    version="0.1.0",
    description="GenMol / DiffDock / MMseqs2 / 结构预测的本地 GPU 推理后端",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (health.router, jobs.router, files.router, tools.router):
    app.include_router(r, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "protein-platform-backend", "docs": "/docs", "health": "/api/health"}
