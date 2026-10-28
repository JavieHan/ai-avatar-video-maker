#!/usr/bin/env python3
"""Place user-provided phrase audio at manually chosen times on a video.

This is post-production replacement, NOT audio-driven lip animation. The caller
must listen, choose the timestamps, and review the resulting mouth movements.
"""
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from muse_common import local_file, probe_video, read_json


def audio_duration(path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
        check=True, capture_output=True, text=True)
    info = json.loads(result.stdout)
    if not any(s.get('codec_type') == 'audio' for s in info.get('streams', [])):
        raise ValueError(f'音频文件没有音轨：{path}')
    duration = float(info.get('format', {}).get('duration', 0))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError(f'无法读取音频时长：{path}')
    return duration


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f'{label} 必须是有限数字')
    return float(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path, help='已剪辑画面，保留视频流，替换原声音频')
    parser.add_argument('plan', type=Path, help='JSON: {"phrases":[{"audio":"a.wav","at":1.0,"rate":1.0}]}')
    parser.add_argument('--out', type=Path, required=True, help='新的 MP4 路径，不覆盖')
    args = parser.parse_args()
    video = local_file(str(args.video), Path.cwd())
    duration = probe_video(video, require_audio=False)['duration']
    plan = read_json(args.plan)
    if not isinstance(plan, dict) or not isinstance(plan.get('phrases'), list) or not plan['phrases']:
        raise ValueError('计划须包含非空 phrases 数组')
    if os.path.lexists(args.out) or args.out.resolve() == video:
        raise ValueError(f'输出已存在或与输入相同，未覆盖：{args.out}')
    pieces = []
    for i, item in enumerate(plan['phrases'], 1):
        if not isinstance(item, dict):
            raise ValueError(f'第 {i} 条语音不是对象')
        source = local_file(item.get('audio'), args.plan.resolve().parent)
        at = number(item.get('at'), f'第 {i} 条 at')
        rate = number(item.get('rate', 1), f'第 {i} 条 rate')
        if at < 0 or not 0.5 <= rate <= 2:
            raise ValueError(f'第 {i} 条 at 须非负、rate 须为 0.5–2')
        end = at + audio_duration(source) / rate
        if end > duration + 0.015:
            raise ValueError(f'第 {i} 条超出视频末尾：{end:.3f}s > {duration:.3f}s')
        pieces.append((source, at, rate, end))
    for prev, curr in zip(sorted(pieces, key=lambda x:x[1]), sorted(pieces, key=lambda x:x[1])[1:]):
        if curr[1] < prev[3] - 0.015:
            raise ValueError('语音片段时间重叠；请调整每句 at 和 rate')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-n', '-i', str(video)]
    for source, _, _, _ in pieces:
        cmd.extend(['-i', str(source)])
    # A duration-matched silent base drives the mixer throughout the full video.
    # This also prevents older FFmpeg versions from ending before delayed inputs.
    filters = [f'anullsrc=r=48000:cl=stereo,atrim=duration={duration:.6f},asetpts=PTS-STARTPTS[base]']
    for i, (_, at, rate, _) in enumerate(pieces, 1):
        delay = round(at * 1000)
        filters.append(f'[{i}:a]atempo={rate:.6f},aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,asetpts=PTS-STARTPTS,adelay={delay}:all=1[a{i}]')
    filters.append('[base]' + ''.join(f'[a{i}]' for i in range(1, len(pieces)+1)) +
                   f'amix=inputs={len(pieces)+1}:duration=first:normalize=0,atrim=duration={duration:.6f}[aout]')
    with tempfile.TemporaryDirectory(prefix='.timed-voice-', dir=args.out.parent) as directory:
        staged = Path(directory) / 'result.mp4'
        cmd.extend(['-filter_complex', ';'.join(filters), '-map', '0:v:0', '-map', '[aout]',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', f'{duration:.6f}',
                    '-movflags', '+faststart', str(staged)])
        subprocess.run(cmd, check=True)
        # Publish exclusively; if another process made the destination, do not touch it.
        os.link(staged, args.out)
    print(f'已生成 {args.out}；画面未重新驱动。请实际听审并检查口型。')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(f'换声暂停：{error}')
