#!/bin/bash
# Copy the clean talking-head template. For a ready-to-render media project, use prepare_edit.py.
# Usage: new_edit.sh huazi-916 <new-project> [--no-install]
set -euo pipefail
TPL="${1:-}"; DST="${2:-}"; MODE="${3:-}"
if [ "$TPL" != "huazi-916" ] || [ -z "$DST" ] || { [ -n "$MODE" ] && [ "$MODE" != "--no-install" ]; }; then
  echo '用法：new_edit.sh huazi-916 <新工程目录> [--no-install]'; exit 1
fi
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/templates/$TPL"
[ -d "$SRC" ] || { echo "模板不存在：$SRC"; exit 1; }
if [ -e "$DST" ] || [ -L "$DST" ]; then echo "不覆盖已有工程：$DST"; exit 1; fi
mkdir -p "$DST"
cp -R "$SRC/." "$DST/"
if [ "$MODE" != "--no-install" ]; then (cd "$DST" && npm install); fi
echo '已复制空白模板。可通过 prepare_edit.py 将用户视频、字幕时间轴和可选音轨准备成新工程。'
