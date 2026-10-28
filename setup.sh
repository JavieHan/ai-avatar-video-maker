#!/usr/bin/env bash
# Configure this checkout only; no installations, login, or generation.
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' '配置失败：需要 Python 3；未修改任何技能配置。' >&2
  exit 1
fi
exec python3 -B "$project_root/scripts/configure_agent.py" "$@"
