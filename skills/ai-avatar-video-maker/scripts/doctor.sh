#!/bin/sh
# Environment check only: no installation, account access or generation.
set -u
missing=0
printf '%s\n' 'Muse 口播 · 本机工具检查'
for tool in python3 ffmpeg ffprobe npm whisper-cli; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '  ✓ %s\n' "$tool"
  else
    printf '  - %s 未找到\n' "$tool"
    missing=1
  fi
done
if command -v node >/dev/null 2>&1; then
  node_version=$(node --version 2>/dev/null) || node_version=''
  node_major=${node_version#v}
  node_major=${node_major%%.*}
  case "$node_major" in
    ''|*[!0-9]*)
      printf '%s\n' '  - 无法确认 Node.js 版本（需要 18+）'
      missing=1
      ;;
    *)
      if [ "$node_major" -ge 18 ]; then
        printf '  ✓ Node.js %s\n' "$node_version"
      else
        printf '  - Node.js %s 低于所需的 18\n' "$node_version"
        missing=1
      fi
      ;;
  esac
else
  printf '%s\n' '  - node 未找到（需要 Node.js 18+）'
  missing=1
fi
if [ -n "${WHISPER_MODEL:-}" ] && [ -f "$WHISPER_MODEL" ]; then
  printf '  ✓ WHISPER_MODEL 指向现有文件\n'
else
  printf '%s\n' '  - 未通过 WHISPER_MODEL 指定现有模型；也可在 assemble 时用 --model'
  missing=1
fi
printf '%s\n' '仅请求准备需要 Python；完整本地剪辑还需 FFmpeg、whisper-cli、模型和 Node。'
printf '%s\n' 'Muse 账号、视频时长、额度、模型和录音驱动能力需在实际界面确认。'
exit "$missing"
