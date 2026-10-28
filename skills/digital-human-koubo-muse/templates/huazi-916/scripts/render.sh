#!/bin/sh
# Render silent picture then mix the original or replacement voice with FFmpeg.
# The independent audio pass avoids the 2048-sample delay observed in this Remotion path.
set -eu
if [ "$#" -lt 1 ]; then
  printf '%s\n' '用法：bash scripts/render.sh <新成片.mp4> [Remotion 其他参数]'
  exit 1
fi
out=$1
shift
case "$out" in *.mp4) ;; *) printf '%s\n' '输出文件需以 .mp4 结尾。' >&2; exit 1;; esac
if [ -e "$out" ] || [ -L "$out" ]; then
  printf '输出已存在，不覆盖：%s\n' "$out" >&2
  exit 1
fi
out_dir=$(dirname "$out")
if [ ! -d "$out_dir" ]; then
  printf '输出目录不存在：%s\n' "$out_dir" >&2
  exit 1
fi
out_dir=$(cd "$out_dir" && pwd)
out="$out_dir/$(basename "$out")"
scratch=$(mktemp -d "$out_dir/.koubo-render.XXXXXX")
cleanup() { python3 -c 'import shutil,sys; shutil.rmtree(sys.argv[1], ignore_errors=True)' "$scratch"; }
trap cleanup EXIT HUP INT TERM
cd "$(dirname "$0")/.."
audio=$(node -p 'const e=require("./src/edit.json"); e.voice || e.video')
music=$(node -p 'const e=require("./src/edit.json"); e.music || ""')
volume=$(node -p 'const e=require("./src/edit.json"); Number(e.musicVolume)')
duration=$(node -p 'const e=require("./src/edit.json"); Number(e.duration)')
if [ ! -f "public/$audio" ]; then printf '音轨不存在：public/%s\n' "$audio" >&2; exit 1; fi
if [ -n "$music" ] && [ ! -f "public/$music" ]; then printf '背景音乐不存在：public/%s\n' "$music" >&2; exit 1; fi
npx remotion render src/index.ts Huazi "$scratch/video.mp4" --concurrency=1 --muted "$@"
if [ -n "$music" ]; then
  ffmpeg -v error -i "$scratch/video.mp4" -i "public/$audio" -i "public/$music" \
    -filter_complex "[1:a]aresample=48000,aformat=channel_layouts=stereo,apad[voice];[2:a]aresample=48000,aformat=channel_layouts=stereo,volume=$volume[bed];[voice][bed]amix=inputs=2:duration=first:normalize=0,atrim=duration=$duration,asetpts=PTS-STARTPTS[a]" \
    -map 0:v:0 -map '[a]' -c:v copy -c:a aac -b:a 192k -t "$duration" -movflags +faststart "$scratch/result.mp4"
else
  ffmpeg -v error -i "$scratch/video.mp4" -i "public/$audio" \
    -filter_complex "[1:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration=$duration,asetpts=PTS-STARTPTS[a]" \
    -map 0:v:0 -map '[a]' -c:v copy -c:a aac -b:a 192k -t "$duration" -movflags +faststart "$scratch/result.mp4"
fi
# Exclusive link fails if another process creates the target during rendering.
python3 - "$scratch/result.mp4" "$out" <<'PY'
import os,sys
try:
    os.link(sys.argv[1],sys.argv[2])
except FileExistsError:
    raise SystemExit(f'输出已存在，不覆盖：{sys.argv[2]}')
PY
printf '已输出：%s\n' "$out"
