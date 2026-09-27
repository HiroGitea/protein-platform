# backend

生物信息学平台的后端：FastAPI + 异步任务队列 + 可插拔的模型引擎。

完整项目说明见[仓库根目录 README](../README.md)。

## 跑起来

```bash
uv sync                                          # 只装 Web 层，很快
uv run uvicorn app.main:app --reload --port 8000
```

- API 文档：http://127.0.0.1:8000/docs
- 状态检查：http://127.0.0.1:8000/api/health

`/api/health` 会告诉你显卡型号、算力、torch 版本，以及每个引擎是否就绪、缺什么。
**排查问题先看这个。**

## 目录结构

```
app/
├── main.py          FastAPI 入口、CORS、启动日志
├── config.py        配置（环境变量前缀 PROTEIN_）
├── schemas.py       所有 API 出入参定义
├── jobs.py          异步任务管理：队列、进度、结果文件
├── gpu.py           显卡探测（torch 没装时退回 nvidia-smi）
├── routers/
│   ├── health.py    GET  /api/health
│   ├── jobs.py      GET  /api/jobs/{id}、取消、下载结果
│   ├── files.py     POST /api/files 上传
│   └── tools.py     POST /api/{engine}/... 提交推理任务
└── engines/
    ├── base.py          引擎抽象 + 就绪检查
    ├── _planned.py      未实现引擎的共同基类
    └── *_engine.py      各模型引擎
```

## 设计要点

**重型依赖延迟导入。** `app/` 顶层不 import torch。引擎的 `required_modules`
只用 `importlib.util.find_spec` 查包在不在，不真正加载。这样没装 GPU 依赖的人
也能启动服务、看到 API 文档、知道自己缺什么。

**推理一律异步。** DiffDock 一次几十秒到几分钟，同步 HTTP 必然超时。
所有推理走 `JobManager`：提交立刻返回 `job_id`，前端轮询 `/api/jobs/{id}`。
阻塞的推理代码用 `run_in_executor` 丢线程池。

**单卡默认串行。** `max_concurrent_jobs=1`。16GB 显存同时跑两个模型很容易 OOM。

**引擎失败 ≠ 请求失败。** 引擎没就绪、推理崩了，都变成任务的 `failed` 状态 +
错误信息，HTTP 请求本身仍是 200。前端只需要处理一种错误路径。

## 装引擎依赖

```bash
uv sync --group genmol     # torch cu128 + transformers + safe-mol + rdkit
uv sync --group dev        # ruff + pytest
```

> Blackwell（RTX 50 系，sm_120）必须 `torch>=2.7`，依赖组已指向 cu128 源。
> 上游 GenMol 写死的 `torch==2.6.0` 在这类卡上会报 no kernel image。

## 测试

```bash
uv run pytest -q
uv run ruff check app tests
```

测试不需要任何 GPU 依赖——它们验证的正是"没装依赖时行为要正确"。
