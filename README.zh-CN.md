<div align="center">

# protein-platform

[English](README.md) · **简体中文** · [日本語](README.ja.md)

一个整合蛋白质结构预测、分子对接、序列搜索和分子生成的生物信息学平台。
通过统一的异步任务 API 连接本地计算资源与 NVIDIA 托管服务，各引擎的支持情况见下表。

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](backend/pyproject.toml)
[![SvelteKit](https://img.shields.io/badge/frontend-SvelteKit-ff3e00.svg)](frontend/package.json)

</div>

## 特点

- **统一任务模型**：所有推理都是异步任务。提交后拿到 `job_id`，轮询进度，下载结果文件。
- **双 provider**：同一个功能可以跑在自己的显卡上，也可以调用官方托管 API。
  没有显卡时先用远程跑通流程，有显卡再切到本地，前端代码不用改。
- **独立的引擎状态检查**：某个引擎缺依赖、缺权重或缺 API key 时，只有它自己报"不可用"并说明原因，
  其它引擎仍可正常使用。

## 功能

| 功能 | 模型 | 本地运行 | 官方托管 API |
|---|---|---|---|
| 分子生成 | GenMol (89M) | ✅ 已实现 | ✅ 已实现 |
| 分子优化 | MolMIM (70M) | 📋 接口预留 | ✅ 已实现 |
| 分子对接 | DiffDock | ✅ 已实现 | ✅ 已实现 |
| 序列搜索 | MMseqs2 | ✅ CPU | — |
| 结构预测 | AlphaFold 2 | NIM 服务适配器 | 远程 NIM 服务适配器 |
| 分子可视化 | Mol* | ✅ 前端完成 | — |

> AlphaFold 2 已接入独立部署的 NIM 服务；公共托管端点已弃用，请按 [配置指南](docs/alphafold2.md) 设置服务地址。
> 本地推理需要安装对应依赖并准备模型权重或数据库，远程推理需要配置 API key。
> Mol* 查看器已接入；推理页面目前仍使用示例数据，接入后端的工作见路线图。
> 可通过下方的 REST API 示例运行推理任务。

## 架构

```
┌──────────────────────────────────────────┐
│  frontend/   SvelteKit + Tailwind + Mol*  │
│  $lib/api/client.ts   提交 / 轮询 / 下载   │
└───────────────────┬──────────────────────┘
                    │ REST
┌───────────────────▼──────────────────────┐
│  backend/    FastAPI                      │
│  ├─ routers/   HTTP 层                    │
│  ├─ jobs.py    异步任务队列（单卡默认串行）│
│  └─ engines/   每个引擎 = local + remote  │
└─────────┬────────────────────┬───────────┘
          ▼                    ▼
    本地 GPU / 二进制      NVIDIA NIM 托管 API
```

provider 选择规则（`.env` 里每个引擎单独配置）：

| 值 | 行为 |
|---|---|
| `auto`（默认） | 本地可用就用本地，否则退到远程 |
| `local` | 只用本地 |
| `remote` | 只用托管 API |

## 快速开始

### 1. 后端

```bash
cd backend
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload --port 8000
```

- API 文档：http://127.0.0.1:8000/docs
- 状态检查：http://127.0.0.1:8000/api/health —— 显卡信息、每个引擎和 provider 的可用性与缺失项

### 2. 前端

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

打开 http://localhost:5173。

### 3a. 用托管 API（无需显卡）

到 [build.nvidia.com](https://build.nvidia.com) 获取有相应模型访问权限的 API key，填入 `backend/.env`：

```bash
NVIDIA_API_KEY=nvapi-xxxxxxxx
```

重启后端，通过 `/api/health` 检查各引擎状态，再通过 REST API 提交任务。

### 3b. 用本地计算资源

以下命令在仓库根目录运行。启用多个模型时，在后续 `uv sync` 命令中保留所有需要的依赖组。

```bash
# GenMol
./scripts/setup-genmol.sh                 # 拉取源码
uv sync --directory backend --group genmol      # torch cu128 等依赖
# 权重放到 backend/checkpoints/model_v2.ckpt

# DiffDock
./scripts/setup-diffdock.sh
uv sync --directory backend --group genmol --group diffdock

# MMseqs2（CPU；此安装脚本适用于 Linux x86_64）
./scripts/setup-mmseqs.sh                 # 安装二进制
export PATH="$PWD/backend/third_party/bin:$PATH"
./scripts/build-mmseqs-db.sh swissprot    # 下载并建库，约 300MB
```

## API 示例

```bash
# 提交
curl -X POST localhost:8000/api/genmol/generate \
     -H 'Content-Type: application/json' \
     -d '{"mode":"denovo","num_samples":10}'
# -> {"job_id":"a1b2c3d4e5f6","status":"queued"}

# 轮询
curl localhost:8000/api/jobs/a1b2c3d4e5f6

# 下载结果
curl -O localhost:8000/api/jobs/a1b2c3d4e5f6/files/molecules.smi
```

| Endpoint | 功能 |
|---|---|
| `GET  /api/health` | 显卡与引擎状态 |
| `POST /api/files` | 上传 PDB / SDF / FASTA |
| `POST /api/genmol/generate` | 分子生成 |
| `POST /api/molmim/optimize` | 分子优化 |
| `POST /api/diffdock/dock` | 分子对接 |
| `POST /api/mmseqs/search` | 序列搜索 |
| `POST /api/fold/predict` | 结构预测 |
| `GET  /api/jobs/{id}` | 任务状态 |
| `GET  /api/jobs/{id}/files/{name}` | 下载结果 |

前端封装：

```ts
import { generateMolecules } from '$lib/api/client';

const result = await generateMolecules(
  { mode: 'denovo', num_samples: 10 },
  (job) => (progress = job.progress)
);
```

## 硬件说明

开发环境：RTX 5070 Ti 16GB（Blackwell, sm_120）、64GB 内存。

> ⚠️ **RTX 50 系（Blackwell）需要 PyTorch ≥ 2.7 + CUDA 12.8。**
> 上游 GenMol 固定了 `torch==2.6.0`，在 50 系显卡上会报
> `no kernel image is available for execution on the device`。
> 本项目的依赖组已改为 `torch>=2.7` 并使用 cu128 源。

AlphaFold 2 的部署要求与环境变量见 [配置指南](docs/alphafold2.md)。

## 第三方模型与许可证

本仓库**不分发**任何第三方代码或权重，由 `scripts/` 下的脚本在本地获取。详见 [NOTICE](NOTICE)。

| 项目 | 代码许可 | 权重许可 |
|---|---|---|
| [GenMol](https://github.com/NVIDIA-Digital-Bio/genmol) | Apache-2.0 | NVIDIA Open Model License |
| [MolMIM](https://github.com/NVIDIA/bionemo-framework) | Apache-2.0 | NVIDIA AI Foundation Models Community License |
| [DiffDock](https://github.com/gcorso/DiffDock) | MIT | MIT |
| [MMseqs2](https://github.com/soedinglab/MMseqs2) | GPLv3 ⚠️ | — |
| [AlphaFold 2](https://github.com/google-deepmind/alphafold) | 见上游许可 | 见上游及 NIM 条款 |
| [Mol*](https://github.com/molstar/molstar) | MIT | — |

MMseqs2 是 GPLv3，本项目只通过子进程调用其命令行，不链接其代码。

## 目录结构

```
protein-platform/
├── backend/     FastAPI 后端（详见 backend/README.md）
├── frontend/    SvelteKit 前端（详见 frontend/README.md）
├── scripts/     第三方源码 / 二进制 / 数据库的获取脚本
└── docs/        模型背景资料
```

## 路线图

- [x] 后端框架：异步任务、双 provider 引擎、GPU 探测、文件上传
- [x] 五个引擎的 local / remote 实现或接口
- [x] 前端 API 客户端
- [ ] 前端各页面接入真实后端，移除 mock 数据
- [x] 接入本地或远程 AlphaFold 2 NIM 服务
- [ ] 用户认证与任务历史

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[Apache-2.0](LICENSE)
