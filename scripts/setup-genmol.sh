#!/usr/bin/env bash
# 拉取 GenMol 上游源码。权重需要另外下载，见脚本末尾提示。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$REPO_ROOT/backend/genmol"

if [ -d "$TARGET/.git" ]; then
    echo "已存在 $TARGET，拉取更新…"
    git -C "$TARGET" pull --ff-only
else
    echo "克隆 GenMol 到 $TARGET …"
    git clone --depth 1 https://github.com/NVIDIA-Digital-Bio/genmol.git "$TARGET"
fi

cat <<'EOF'

源码就绪。接下来：

1. 装依赖：
     cd backend && uv sync --group genmol

2. 下载权重（二选一）：
   - HuggingFace（免登录，推荐）
       https://huggingface.co/nvidia/NV-GenMol-89M-v2
   - NGC（需要 API key）
       https://catalog.ngc.nvidia.com/orgs/nvidia/teams/clara/resources/genmol_v2

   把 ckpt 放到 backend/checkpoints/model_v2.ckpt

3. 确认就绪：
     curl http://127.0.0.1:8000/api/health | jq '.engines[] | select(.name=="genmol")'

注意：本项目不使用上游的 env/setup.sh —— 它写死 torch==2.6.0，
在 Blackwell(sm_120) 显卡上无法运行。依赖统一由 backend/pyproject.toml 管理。
EOF
