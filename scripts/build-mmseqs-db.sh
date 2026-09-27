#!/usr/bin/env bash
# 下载并建立 MMseqs2 搜索数据库。
#
# 用法: ./scripts/build-mmseqs-db.sh <数据库名>
#   swissprot  约 300MB   手工注释，适合做演示
#   uniref50   约 15GB    常用
#   uniref90   约 60GB    大
set -euo pipefail

DB="${1:-}"
if [ -z "$DB" ]; then
    echo "用法: $0 <swissprot|uniref50|uniref90|pdb|...>"
    echo "完整列表: mmseqs databases"
    exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_DIR="$REPO_ROOT/backend/databases"
MMSEQS="${PROTEIN_MMSEQS_BINARY:-mmseqs}"

command -v "$MMSEQS" >/dev/null 2>&1 || {
    echo "找不到 mmseqs，先跑 scripts/setup-mmseqs.sh"; exit 1;
}

mkdir -p "$DB_DIR"
echo "下载并建立 $DB（这一步可能很久，数据库大的话以小时计）…"
"$MMSEQS" databases "$DB" "$DB_DIR/$DB" "$DB_DIR/tmp_$DB"
rm -rf "$DB_DIR/tmp_$DB"

echo
echo "完成。后端会自动发现 $DB_DIR/$DB"
echo "确认: curl -s localhost:8000/api/health | jq '.engines[] | select(.name==\"mmseqs\")'"
