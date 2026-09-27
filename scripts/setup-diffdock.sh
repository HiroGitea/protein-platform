#!/usr/bin/env bash
# 拉取 DiffDock 源码。不下载权重——上游仓库自带训练好的模型在 workdir/ 下。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$REPO_ROOT/backend/third_party/DiffDock"

mkdir -p "$(dirname "$TARGET")"
if [ -d "$TARGET/.git" ]; then
    echo "已存在 $TARGET，拉取更新…"
    git -C "$TARGET" pull --ff-only
else
    echo "克隆 DiffDock 到 $TARGET …"
    git clone --depth 1 https://github.com/gcorso/DiffDock.git "$TARGET"
fi

cat <<'EOF'

源码就绪。接下来：

1. 装依赖：
     cd backend && uv sync --group diffdock

   注意 torch-geometric 系列（torch-scatter / torch-sparse）需要和 torch 的
   CUDA 版本匹配。Blackwell(sm_120) 用 cu128 轮子：
     uv pip install torch-scatter torch-sparse \
       -f https://data.pyg.org/whl/torch-2.7.0+cu128.html

2. 首次推理会自动下载 ESM2 embedding 权重（约 1.5GB）。

3. 确认就绪：
     curl -s localhost:8000/api/health | jq '.engines[] | select(.name=="diffdock")'

不想折腾本地环境的话，把 PROTEIN_DIFFDOCK_PROVIDER=remote 写进 .env，
直接用 build.nvidia.com 的托管 API。
EOF
