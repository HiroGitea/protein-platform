#!/usr/bin/env bash
# 安装 MMseqs2 二进制。只装工具本身，不下载任何数据库。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="$REPO_ROOT/backend/third_party/bin"

if command -v mmseqs >/dev/null 2>&1; then
    echo "系统里已有 mmseqs: $(command -v mmseqs)"
    mmseqs version
    exit 0
fi

mkdir -p "$BIN_DIR"
cd "$(mktemp -d)"

# 挑一个当前 CPU 支持的构建。avx2 覆盖绝大多数现代 x86_64
BUILD="mmseqs-linux-avx2.tar.gz"
grep -q avx2 /proc/cpuinfo || BUILD="mmseqs-linux-sse41.tar.gz"
echo "下载 $BUILD …"

curl -fsSL "https://mmseqs.com/latest/$BUILD" -o mmseqs.tar.gz
tar xzf mmseqs.tar.gz
install -m 755 mmseqs/bin/mmseqs "$BIN_DIR/mmseqs"

cat <<EOF

已安装到 $BIN_DIR/mmseqs

把它加进 PATH：
    export PATH="$BIN_DIR:\$PATH"
或在 backend/.env 里写绝对路径：
    PROTEIN_MMSEQS_BINARY=$BIN_DIR/mmseqs

然后建库（数据库要另外下载，见 scripts/build-mmseqs-db.sh）：
    ./scripts/build-mmseqs-db.sh swissprot

注意：MMseqs2 是 GPLv3。本项目通过子进程调用它，不链接其代码。
EOF
