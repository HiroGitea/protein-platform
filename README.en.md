<div align="center">

# protein-platform

[中文](README.md) · **English** · [日本語](README.ja.md)

A bioinformatics platform that brings protein structure prediction, molecular docking,
sequence search and molecular generation together in one place.
Every model can run on either a **local GPU** or an **official hosted API**, switchable at any time.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](backend/pyproject.toml)
[![SvelteKit](https://img.shields.io/badge/frontend-SvelteKit-ff3e00.svg)](frontend/package.json)

</div>

## Highlights

- **One job model for everything**: every inference runs as an async job. Submit, get a `job_id`,
  poll progress, download result files.
- **Two providers per engine**: the same feature can run on your own GPU or call a hosted API.
  Get the workflow running remotely first, switch to local once you have a GPU. The frontend doesn't change.
- **Honest failures**: when an engine is missing dependencies, weights or an API key, only that engine
  reports "unavailable" along with the reason. It won't take the service down, and it **never returns fake data**.

## Features

| Feature | Model | Local GPU | Hosted API |
|---|---|---|---|
| Molecule generation | GenMol (89M) | ✅ Implemented | ✅ Implemented |
| Molecule optimization | MolMIM (70M) | 📋 Interface only | ✅ Implemented |
| Molecular docking | DiffDock | ✅ Implemented | ✅ Implemented |
| Sequence search | MMseqs2 | ✅ Implemented | — |
| Structure prediction | ESMFold | 📋 Interface only | ✅ Implemented |
| Molecule viewer | Mol* | ✅ Frontend done | — |

> This is a showcase project. The code and interfaces are complete, but local inference needs you to
> download weights and databases yourself, and remote inference needs your own API key.
> Not every combination has been tested end to end.

## Architecture

```
┌──────────────────────────────────────────┐
│  frontend/   SvelteKit + Tailwind + Mol*  │
│  $lib/api/client.ts   submit/poll/download│
└───────────────────┬──────────────────────┘
                    │ REST
┌───────────────────▼──────────────────────┐
│  backend/    FastAPI                      │
│  ├─ routers/   HTTP layer                 │
│  ├─ jobs.py    async job queue (serial on │
│  │             a single GPU by default)   │
│  └─ engines/   each engine = local+remote │
└─────────┬────────────────────┬───────────┘
          ▼                    ▼
   local GPU / binary     NVIDIA NIM hosted API
```

Provider selection (set per engine in `.env`):

| Value | Behavior |
|---|---|
| `auto` (default) | Use local if available, otherwise fall back to remote |
| `local` | Local only |
| `remote` | Hosted API only |

## Quick start

### 1. Backend

```bash
cd backend
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload --port 8000
```

- API docs: http://127.0.0.1:8000/docs
- Status: http://127.0.0.1:8000/api/health shows GPU info, plus availability and what's missing for every engine and provider

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173.

### 3a. Use the hosted API (no GPU needed)

Get a free API key at [build.nvidia.com](https://build.nvidia.com) and put it in `backend/.env`:

```bash
NVIDIA_API_KEY=nvapi-xxxxxxxx
```

Restart the backend. GenMol, MolMIM, DiffDock and structure prediction are now available.

### 3b. Use a local GPU

```bash
# GenMol
./scripts/setup-genmol.sh                 # fetch source
cd backend && uv sync --group genmol      # torch cu128 and friends
# put the weights at backend/checkpoints/model_v2.ckpt

# DiffDock
./scripts/setup-diffdock.sh
cd backend && uv sync --group diffdock

# MMseqs2 (CPU)
./scripts/setup-mmseqs.sh                 # install binary
./scripts/build-mmseqs-db.sh swissprot    # download and build, ~300MB
```

## API example

```bash
# submit
curl -X POST localhost:8000/api/genmol/generate \
     -H 'Content-Type: application/json' \
     -d '{"mode":"denovo","num_samples":10}'
# -> {"job_id":"a1b2c3d4e5f6","status":"queued"}

# poll
curl localhost:8000/api/jobs/a1b2c3d4e5f6

# download
curl -O localhost:8000/api/jobs/a1b2c3d4e5f6/files/molecules.smi
```

| Endpoint | Purpose |
|---|---|
| `GET  /api/health` | GPU and engine status |
| `POST /api/files` | Upload PDB / SDF / FASTA |
| `POST /api/genmol/generate` | Molecule generation |
| `POST /api/molmim/optimize` | Molecule optimization |
| `POST /api/diffdock/dock` | Molecular docking |
| `POST /api/mmseqs/search` | Sequence search |
| `POST /api/fold/predict` | Structure prediction |
| `GET  /api/jobs/{id}` | Job status |
| `GET  /api/jobs/{id}/files/{name}` | Download a result |

From the frontend:

```ts
import { generateMolecules } from '$lib/api/client';

const result = await generateMolecules(
  { mode: 'denovo', num_samples: 10 },
  (job) => (progress = job.progress)
);
```

## Hardware notes

Developed on an RTX 5070 Ti 16GB (Blackwell, sm_120) with 64GB RAM.

> ⚠️ **RTX 50 series (Blackwell) needs PyTorch ≥ 2.7 with CUDA 12.8.**
> Upstream GenMol pins `torch==2.6.0`, which fails on 50-series cards with
> `no kernel image is available for execution on the device`.
> This project's dependency groups use `torch>=2.7` from the cu128 index instead.

Structure prediction uses ESMFold rather than full AlphaFold2/OpenFold. The latter's MSA databases
are over 2TB, which isn't practical on a single-GPU machine.

## Third-party models and licenses

This repository **does not redistribute** any third-party code or weights. The scripts under
`scripts/` fetch them locally. See [NOTICE](NOTICE).

| Project | Code license | Weights license |
|---|---|---|
| [GenMol](https://github.com/NVIDIA-Digital-Bio/genmol) | Apache-2.0 | NVIDIA Open Model License |
| [MolMIM](https://github.com/NVIDIA/bionemo-framework) | Apache-2.0 | NVIDIA AI Foundation Models Community License |
| [DiffDock](https://github.com/gcorso/DiffDock) | MIT | MIT |
| [MMseqs2](https://github.com/soedinglab/MMseqs2) | GPLv3 ⚠️ | — |
| [ESMFold](https://github.com/facebookresearch/esm) | MIT | MIT |
| [Mol*](https://github.com/molstar/molstar) | MIT | — |

MMseqs2 is GPLv3. This project only invokes its command-line binary as a subprocess and does not link against its code.

## Layout

```
protein-platform/
├── backend/     FastAPI backend (see backend/README.md)
├── frontend/    SvelteKit frontend (see frontend/README.md)
├── scripts/     fetch scripts for third-party source, binaries and databases
└── docs/        model background notes
```

## Roadmap

- [x] Backend framework: async jobs, dual-provider engines, GPU detection, uploads
- [x] Local/remote implementations or interfaces for all five engines
- [x] Frontend API client
- [ ] Wire every frontend page to the real backend and remove the mock data
- [ ] Local ESMFold implementation
- [ ] User authentication and job history

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) (in Chinese).

## License

[Apache-2.0](LICENSE)
