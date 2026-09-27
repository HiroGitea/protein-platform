# protein-platform

> 一个把蛋白质结构预测、分子对接、序列搜索和分子生成整合到一起的生物信息学平台。
> 每个模型都支持**本地 GPU 推理**和**官方托管 API** 两种后端，可以按需切换。
>
> *A bioinformatics platform integrating protein structure prediction, molecular docking,
> sequence search and molecular generation — each with both local-GPU and hosted-API backends.*

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](backend/pyproject.toml)
[![SvelteKit](https://img.shields.io/badge/frontend-SvelteKit-ff3e00.svg)](frontend/package.json)

## 这个项目解决什么问题

大部分生物信息学模型（DiffDock、ESMFold、GenMol……）各有各的环境、各有各的调用方式，
装起来痛苦，跑起来更痛苦。这个项目把它们收到一个统一的 Web 界面和一套统一的 REST API 后面：

- **统一任务模型**：所有推理都是异步任务，提交拿 `job_id`，轮询进度，取结果文件。
- **双 provider**：同一个引擎既能跑在你自己的显卡上，也能调官方托管 API。
  没有显卡先用远程跑通流程，有显卡再切本地，前端代码一行不用改。
- **不装就不碍事**：某个引擎缺依赖或缺权重，只是它自己报"未就绪"并说明缺什么，
  不会拖垮整个服务。

## 当前状态

这个项目正在开发中。**没有任何功能会返回假数据**——引擎没就绪就明确报未就绪。

| 功能 | 本地 GPU | 官方托管 API | 前端页面 |
|---|---|---|---|
| 分子可视化 (Mol*) | — | — | ✅ 可用 |
| GenMol 分子生成 | 🚧 引擎已写，待权重 | 🚧 开发中 | 🚧 待接入 |
| MolMIM 分子优化 | 📋 接口预留 | 🚧 开发中 | 🚧 待接入 |
| DiffDock 分子对接 | 🚧 开发中 | 🚧 开发中 | 🚧 待接入 |
| MMseqs2 序列搜索 | 🚧 开发中 | 📋 计划中 | 🚧 待接入 |
| 蛋白质结构预测 | 📋 接口预留 (ESMFold) | 🚧 开发中 | 🚧 待接入 |
| 用户认证 | 📋 计划中 | — | ⚠️ 仅前端占位 |

✅ 可用 · 🚧 开发中 · 📋 计划中 · ⚠️ 未完成

## 架构

```
┌─────────────────────────────────────────┐
│  frontend/   SvelteKit + Tailwind + Mol* │
│  $lib/api/client.ts  ── 提交任务/轮询/下载 │
└──────────────────┬──────────────────────┘
                   │ REST (JSON + multipart)
┌──────────────────▼──────────────────────┐
│  backend/    FastAPI                     │
│  ├─ routers/   HTTP 层                   │
│  ├─ jobs.py    异步任务队列（单卡默认串行）│
│  └─ engines/   引擎层                    │
│       每个引擎 = local provider (GPU)     │
│                + remote provider (官方API)│
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   本地 GPU 推理          官方托管 API
   torch / 二进制         NVIDIA NIM 等
```

重型依赖（torch 等）**延迟导入**：服务启动时不加载，所以没装 GPU 依赖也能跑起来。

## 硬件要求

本地推理这条路最低要一张 NVIDIA 显卡。开发使用的配置：

- **GPU**: RTX 5070 Ti 16GB（Blackwell, sm_120）
- **内存**: 64GB
- **存储**: 模型权重几 GB；MMseqs2 数据库从几百 MB（SwissProt）到几十 GB（UniRef50）不等

> ⚠️ **Blackwell 用户注意**：`sm_120` 需要 **PyTorch ≥ 2.7 + CUDA 12.8**。
> 上游 GenMol 仓库写死了 `torch==2.6.0`，在 50 系显卡上会报
> `no kernel image is available for execution on the device`。
> 本项目的依赖组已经改用 `torch>=2.7` 并指向 cu128 源。

只用托管 API 的话不需要显卡。

## 快速开始

### 后端

```bash
cd backend
uv sync                      # 只装 Web 层依赖，很快
uv run uvicorn app.main:app --reload --port 8000
```

打开 http://127.0.0.1:8000/docs 看 API 文档，
或 http://127.0.0.1:8000/api/health 看显卡和各引擎状态。

按需装引擎依赖：

```bash
uv sync --group genmol       # GenMol 本地推理（含 torch cu128）
uv sync --group diffdock     # DiffDock 本地推理
uv sync --group fold         # ESMFold 本地推理
```

### 前端

```bash
cd frontend
npm install
cp .env.example .env         # 配置后端地址
npm run dev
```

打开 http://localhost:5173。

### 使用托管 API（无需显卡）

在 `backend/.env` 里填上 API key，把对应引擎的 provider 切成 `remote`：

```bash
cp backend/.env.example backend/.env
```

## API 用法

所有推理都是异步任务：

```bash
# 1. 提交
curl -X POST http://127.0.0.1:8000/api/genmol/generate \
     -H 'Content-Type: application/json' \
     -d '{"mode":"denovo","num_samples":10}'
# -> {"job_id":"a1b2c3d4e5f6","status":"queued"}

# 2. 轮询
curl http://127.0.0.1:8000/api/jobs/a1b2c3d4e5f6
# -> {"status":"running","progress":0.3,"message":"生成分子",...}

# 3. 取结果文件
curl -O http://127.0.0.1:8000/api/jobs/a1b2c3d4e5f6/files/molecules.smi
```

前端用 `$lib/api/client.ts` 封装好了，一行搞定：

```ts
import { generateMolecules } from '$lib/api/client';

const result = await generateMolecules(
  { mode: 'denovo', num_samples: 10 },
  (job) => (progress = job.progress)   // 进度回调
);
```

## 集成的模型

本仓库**不分发**任何第三方代码或权重，由安装脚本在本地获取。各自许可证见 [NOTICE](NOTICE)。

| 模型 | 用途 | 代码许可 | 权重许可 |
|---|---|---|---|
| [GenMol](https://github.com/NVIDIA-Digital-Bio/genmol) | 分子生成，89M | Apache-2.0 | NVIDIA Open Model License |
| [MolMIM](https://github.com/NVIDIA/bionemo-framework) | 分子优化，70M | Apache-2.0 | NVIDIA AI Foundation Models Community License |
| [DiffDock](https://github.com/gcorso/DiffDock) | 分子对接 | MIT | MIT |
| [MMseqs2](https://github.com/soedinglab/MMseqs2) | 序列搜索 | GPLv3 ⚠️ | — |
| [ESMFold](https://github.com/facebookresearch/esm) | 结构预测 | MIT | MIT |
| [Mol*](https://github.com/molstar/molstar) | 3D 可视化 | MIT | — |

> ⚠️ MMseqs2 是 GPLv3。本项目通过**子进程调用其命令行二进制**，不链接其代码，
> 因此不影响本仓库的 Apache-2.0 许可。如果你要重新分发，请自行确认合规性。

## 为什么不用完整的 AlphaFold2/OpenFold

完整 AlphaFold2 的 MSA 数据库要 2TB 起步，下载以天计，对单卡场景不合适。
本项目默认走 **ESMFold**（无需 MSA，单卡可跑）或官方托管 API。
如果你确实需要 MSA-based 预测，ColabFold 把 MSA 步骤放到远程，是更现实的折中。

## 路线图

- [x] 后端框架：异步任务、引擎抽象、GPU 探测、文件上传
- [x] 前端 API 客户端
- [ ] GenMol：本地 + 远程双 provider 跑通
- [ ] DiffDock：本地 + 远程
- [ ] MMseqs2：本地二进制 + 建库脚本
- [ ] ESMFold：远程优先，本地接口预留
- [ ] MolMIM：远程优先，本地接口预留
- [ ] 前端六个页面接真实后端，删掉所有 mock
- [ ] 真实用户认证与任务历史

## 贡献

见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[Apache-2.0](LICENSE)
