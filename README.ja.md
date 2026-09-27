<div align="center">

# protein-platform

[English](README.md) · [简体中文](README.zh-CN.md) · **日本語**

タンパク質の構造予測、分子ドッキング、配列検索、分子生成をひとつにまとめた
バイオインフォマティクスプラットフォームです。
各モデルは**ローカル GPU** と**公式ホスト API** のどちらでも実行でき、いつでも切り替えられます。

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](backend/pyproject.toml)
[![SvelteKit](https://img.shields.io/badge/frontend-SvelteKit-ff3e00.svg)](frontend/package.json)

</div>

## 特徴

- **統一されたジョブモデル**：推論はすべて非同期ジョブとして実行されます。
  投入すると `job_id` が返り、進捗をポーリングして結果ファイルをダウンロードします。
- **エンジンごとに 2 つのプロバイダー**：同じ機能を自分の GPU でも、ホスト API でも実行できます。
  GPU がなければまずリモートで一通り動かし、GPU を用意できたらローカルに切り替えます。
  フロントエンドのコードは変わりません。
- **足りないものを正直に報告**：依存関係・重み・API キーが欠けているエンジンは、
  そのエンジンだけが「利用不可」と理由を返します。サービス全体は止まらず、
  **偽のデータを返すこともありません**。

## 機能

| 機能 | モデル | ローカル GPU | ホスト API |
|---|---|---|---|
| 分子生成 | GenMol (89M) | ✅ 実装済み | ✅ 実装済み |
| 分子最適化 | MolMIM (70M) | 📋 インターフェースのみ | ✅ 実装済み |
| 分子ドッキング | DiffDock | ✅ 実装済み | ✅ 実装済み |
| 配列検索 | MMseqs2 | ✅ 実装済み | — |
| 構造予測 | AlphaFold 2 | NIM サービス接続 | リモート NIM サービス接続 |
| 分子ビューア | Mol* | ✅ フロントエンド完成 | — |

> AlphaFold 2 は独立した NIM サービスに接続します。公開 API は廃止予定のため、[設定ガイド](docs/alphafold2.md) に従って接続先を指定してください。
> ローカル推論には依存関係のインストールと、重み・データベースの準備が必要です。
> リモート推論には各自の API キーが必要です。すべての組み合わせを実際に検証したわけではありません。

## アーキテクチャ

```
┌──────────────────────────────────────────┐
│  frontend/   SvelteKit + Tailwind + Mol*  │
│  $lib/api/client.ts  投入 / ポーリング / DL │
└───────────────────┬──────────────────────┘
                    │ REST
┌───────────────────▼──────────────────────┐
│  backend/    FastAPI                      │
│  ├─ routers/   HTTP 層                    │
│  ├─ jobs.py    非同期ジョブキュー          │
│  │             （単一 GPU では既定で直列） │
│  └─ engines/   各エンジン = local + remote │
└─────────┬────────────────────┬───────────┘
          ▼                    ▼
  ローカル GPU / バイナリ   NVIDIA NIM ホスト API
```

プロバイダーの選択（`.env` でエンジンごとに設定）：

| 値 | 動作 |
|---|---|
| `auto`（既定） | ローカルが使えればローカル、使えなければリモートにフォールバック |
| `local` | ローカルのみ |
| `remote` | ホスト API のみ |

## クイックスタート

### 1. バックエンド

```bash
cd backend
uv sync
cp .env.example .env
uv run uvicorn app.main:app --reload --port 8000
```

- API ドキュメント：http://127.0.0.1:8000/docs
- 状態確認：http://127.0.0.1:8000/api/health で GPU 情報と、各エンジン・プロバイダーの利用可否および不足項目を確認できます

### 2. フロントエンド

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

http://localhost:5173 を開きます。

### 3a. ホスト API を使う（GPU 不要）

[build.nvidia.com](https://build.nvidia.com) で無料の API キーを取得し、`backend/.env` に設定します：

```bash
NVIDIA_API_KEY=nvapi-xxxxxxxx
```

バックエンドを再起動し、GenMol・MolMIM・DiffDock の状態を確認してください。AlphaFold 2 は別途サービスの設定が必要です。

### 3b. ローカル GPU を使う

```bash
# GenMol
./scripts/setup-genmol.sh                 # ソースを取得
cd backend && uv sync --group genmol      # torch cu128 などの依存関係
# 重みを backend/checkpoints/model_v2.ckpt に配置

# DiffDock
./scripts/setup-diffdock.sh
cd backend && uv sync --group diffdock

# MMseqs2（CPU）
./scripts/setup-mmseqs.sh                 # バイナリをインストール
./scripts/build-mmseqs-db.sh swissprot    # ダウンロードして構築、約 300MB
```

## API の例

```bash
# 投入
curl -X POST localhost:8000/api/genmol/generate \
     -H 'Content-Type: application/json' \
     -d '{"mode":"denovo","num_samples":10}'
# -> {"job_id":"a1b2c3d4e5f6","status":"queued"}

# ポーリング
curl localhost:8000/api/jobs/a1b2c3d4e5f6

# 結果のダウンロード
curl -O localhost:8000/api/jobs/a1b2c3d4e5f6/files/molecules.smi
```

| エンドポイント | 用途 |
|---|---|
| `GET  /api/health` | GPU とエンジンの状態 |
| `POST /api/files` | PDB / SDF / FASTA のアップロード |
| `POST /api/genmol/generate` | 分子生成 |
| `POST /api/molmim/optimize` | 分子最適化 |
| `POST /api/diffdock/dock` | 分子ドッキング |
| `POST /api/mmseqs/search` | 配列検索 |
| `POST /api/fold/predict` | 構造予測 |
| `GET  /api/jobs/{id}` | ジョブの状態 |
| `GET  /api/jobs/{id}/files/{name}` | 結果のダウンロード |

フロントエンドからの呼び出し：

```ts
import { generateMolecules } from '$lib/api/client';

const result = await generateMolecules(
  { mode: 'denovo', num_samples: 10 },
  (job) => (progress = job.progress)
);
```

## ハードウェアについて

開発環境：RTX 5070 Ti 16GB（Blackwell, sm_120）、メモリ 64GB。

> ⚠️ **RTX 50 シリーズ（Blackwell）には PyTorch 2.7 以上と CUDA 12.8 が必要です。**
> 上流の GenMol は `torch==2.6.0` に固定されており、50 シリーズでは
> `no kernel image is available for execution on the device` で失敗します。
> 本プロジェクトの依存グループは `torch>=2.7` と cu128 インデックスを使うよう変更済みです。

AlphaFold 2 の導入手順は [設定ガイド](docs/alphafold2.md) を参照してください。

## サードパーティのモデルとライセンス

本リポジトリはサードパーティのコードや重みを**再配布しません**。
`scripts/` 以下のスクリプトがローカルに取得します。詳細は [NOTICE](NOTICE) を参照してください。

| プロジェクト | コードのライセンス | 重みのライセンス |
|---|---|---|
| [GenMol](https://github.com/NVIDIA-Digital-Bio/genmol) | Apache-2.0 | NVIDIA Open Model License |
| [MolMIM](https://github.com/NVIDIA/bionemo-framework) | Apache-2.0 | NVIDIA AI Foundation Models Community License |
| [DiffDock](https://github.com/gcorso/DiffDock) | MIT | MIT |
| [MMseqs2](https://github.com/soedinglab/MMseqs2) | GPLv3 ⚠️ | — |
| [AlphaFold 2](https://github.com/google-deepmind/alphafold) | 上流のライセンスを参照 | 上流および NIM の利用規約を参照 |
| [Mol*](https://github.com/molstar/molstar) | MIT | — |

MMseqs2 は GPLv3 です。本プロジェクトはそのコマンドラインバイナリをサブプロセスとして呼び出すだけで、コードにはリンクしていません。

## ディレクトリ構成

```
protein-platform/
├── backend/     FastAPI バックエンド（backend/README.md を参照）
├── frontend/    SvelteKit フロントエンド（frontend/README.md を参照）
├── scripts/     サードパーティのソース・バイナリ・データベースの取得スクリプト
└── docs/        モデルの背景資料
```

## ロードマップ

- [x] バックエンド基盤：非同期ジョブ、デュアルプロバイダーのエンジン、GPU 検出、アップロード
- [x] 5 つのエンジンの local / remote 実装またはインターフェース
- [x] フロントエンドの API クライアント
- [ ] フロントエンドの各ページを実際のバックエンドにつなぎ、モックデータを削除
- [x] ローカル・リモート AlphaFold 2 NIM サービスへの接続
- [ ] ユーザー認証とジョブ履歴

## コントリビューション

[CONTRIBUTING.md](CONTRIBUTING.md)（中国語）を参照してください。

## ライセンス

[Apache-2.0](LICENSE)
