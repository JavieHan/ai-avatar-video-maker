#!/bin/sh
# Environment check only: no installation, account access or generation.
set -u
missing=0
printf '%s\n' 'Muse 口播 · 本机工具检查'
for tool in python3 ffmpeg ffprobe node npm whisper-cli; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '  ✓ %s\n' "$tool"
  else
    printf '  - %s 未找到\n' "$tool"
    missing=1
  fi
done
if [ -n "${WHISPER_MODEL:-}" ] && [ -f "$WHISPER_MODEL" ]; then
  printf '  ✓ WHISPER_MODEL 指向现有文件\n'
else
  printf '%s\n' '  - 未通过 WHISPER_MODEL 指定现有模型；也可在 assemble 时用 --model'
fi
printf '%s\n' '仅请求准备需要 Python；完整本地剪辑还需 FFmpeg、whisper-cli、模型和 Node。'
printf '%s\n' 'Muse 账号、视频时长、额度、模型和录音驱动能力需在实际界面确认。'
exit "$missing"
