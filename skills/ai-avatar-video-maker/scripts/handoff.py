#!/usr/bin/env python3
"""Prepare a manual Muse tail-frame handoff; no generation or network calls.

The user chooses a retained duration after reviewing speech and expression. The
script makes a new 30 fps audiovisual cut, extracts its actual last frame, and
writes a separate task list that binds the next request to that image. The image
is a reference: this does not establish a hard first-frame lock.
"""
import argparse
import copy
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from muse_common import file_hash, probe_video, read_json, segment_id, task_hash, write_json

FPS = 30


def run(command):
    return subprocess.run(command, check=True, capture_output=True)


def no_existing_outputs(paths):
    # Resolve the directory only, never follow a final-component symlink.
    resolved = [p.expanduser().absolute().parent.resolve() / p.expanduser().name for p in paths]
    if len(set(resolved)) != len(resolved):
        raise ValueError('输出路径不能重复')
    for path in resolved:
        if os.path.lexists(path):
            raise ValueError(f'输出已存在，不覆盖：{path}')
        if not path.parent.is_dir():
            raise ValueError(f'输出目录不存在：{path.parent}')
    return resolved


def frames_count(path):
    import json
    probe = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
                 '-show_entries', 'stream=nb_read_frames', '-of', 'json', str(path)])
    return int(json.loads(probe.stdout)['streams'][0]['nb_read_frames'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', required=True, type=Path, help='经用户检查的上一段原片')
    parser.add_argument('--keep-seconds', required=True, type=float, help='人工选择保留时长（秒），向下取整至30fps帧边界')
    parser.add_argument('--trimmed', required=True, type=Path, help='新导出的保留段 MP4')
    parser.add_argument('--tail', required=True, type=Path, help='新导出的实际尾帧 PNG')
    parser.add_argument('--tasks', required=True, type=Path, help='当前离线 tasks.json')
    parser.add_argument('--next-id', required=True, help='需要续接的下一段 id')
    parser.add_argument('--output-tasks', required=True, type=Path, help='新的离线任务清单，不覆盖旧文件')
    args = parser.parse_args()
    source = args.video.expanduser().resolve()
    if not source.is_file():
        raise ValueError(f'找不到上一段视频：{source}')
    if args.trimmed.suffix.lower() != '.mp4' or args.tail.suffix.lower() != '.png' or args.output_tasks.suffix.lower() != '.json':
        raise ValueError('输出文件扩展名必须依次为 .mp4、.png、.json')
    video_out, tail_out, tasks_out = no_existing_outputs([args.trimmed, args.tail, args.output_tasks])
    source_tasks = args.tasks.expanduser().resolve()
    if not source_tasks.is_file():
        raise ValueError(f'找不到任务清单：{source_tasks}')
    if not math.isfinite(args.keep_seconds) or args.keep_seconds <= 0:
        raise ValueError('保留时长必须为正数')
    nframes = math.floor(args.keep_seconds * FPS + 1e-7)
    if nframes < 1:
        raise ValueError('保留时长不足一帧')
    seconds = nframes / FPS
    source_info = probe_video(source)
    if seconds > source_info['duration'] + 1e-6:
        raise ValueError(f'保留时长超过视频长度 {source_info["duration"]:.3f} 秒')
    request = read_json(source_tasks)
    if not isinstance(request, dict) or request.get('provider') != 'muse' or not isinstance(request.get('tasks'), list):
        raise ValueError('需要有效 Muse 离线任务清单')
    tasks = request['tasks']
    ids = [segment_id(task.get('id')) for task in tasks]
    if len(set(ids)) != len(ids):
        raise ValueError('任务段号重复')
    next_id = segment_id(args.next_id)
    if next_id not in ids or ids.index(next_id) == 0:
        raise ValueError('下一段必须是清单中第一段之后的有效段号')
    idx = ids.index(next_id)
    old = tasks[idx]
    if old.get('status') != 'prepared_not_generated':
        raise ValueError('下一段不是待生成状态；请勿修改已提交或已完成任务')
    task_hash(old)  # Fail early if its previously bound image changed.
    previous_id = ids[idx - 1]
    video_hash = file_hash(source)

    # Stage each file beside its final destination, then publish with no-clobber
    # hard links. If any step fails, remove only links created by this invocation.
    created = []
    with tempfile.TemporaryDirectory(prefix='.handoff-', dir=video_out.parent) as vd, \
         tempfile.TemporaryDirectory(prefix='.handoff-', dir=tail_out.parent) as td, \
         tempfile.TemporaryDirectory(prefix='.handoff-', dir=tasks_out.parent) as jd:
        staged_video = Path(vd) / 'trim.mp4'
        staged_tail = Path(td) / 'tail.png'
        staged_tasks = Path(jd) / 'tasks.json'
        t = f'{seconds:.9f}'
        run(['ffmpeg', '-v', 'error', '-i', str(source), '-filter_complex',
             f'[0:v:0]fps={FPS},trim=end_frame={nframes},setpts=PTS-STARTPTS[v];'
             f'[0:a:0]atrim=duration={t},asetpts=PTS-STARTPTS[a]',
             '-map', '[v]', '-map', '[a]', '-frames:v', str(nframes), '-t', t,
             '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
             '-b:a', '192k', '-ar', '48000', '-ac', '2', '-movflags', '+faststart', str(staged_video)])
        probe_video(staged_video)
        if frames_count(staged_video) != nframes:
            raise ValueError('剪后实际帧数不足，未输出；请确认选点在视频画面范围内')
        run(['ffmpeg', '-v', 'error', '-i', str(staged_video), '-vf', f'select=eq(n\\,{nframes - 1})',
             '-frames:v', '1', '-fps_mode', 'vfr', str(staged_tail)])
        if not staged_tail.is_file() or staged_tail.stat().st_size == 0:
            raise ValueError('未能提取剪后片段的实际尾帧')
        updated = copy.deepcopy(request)
        task = updated['tasks'][idx]
        task['reference_image'] = str(tail_out)
        task['reference_image_sha256'] = file_hash(staged_tail)
        task['handoff'] = {'previous_id': previous_id, 'source_video_sha256': video_hash,
                           'retained_video': str(video_out), 'retained_frames': nframes,
                           'fps': FPS, 'reference_kind': 'last_frame_image_reference',
                           'source_match_verified': False, 'first_frame_locked': False}
        task['prompt'] = ('承接前一段：请使用实际附上的上一段剪后尾帧图片作为参考；'
                          '保持同一人物的脸、头部倾角、视线、肩部、服装、背景、光线及固定机位，'
                          '从参考画面的状态自然继续。图片是参考，不保证硬首帧锁定。\n' + task['prompt'])
        write_json(staged_tasks, updated)
        try:
            for staged, final in ((staged_video, video_out), (staged_tail, tail_out), (staged_tasks, tasks_out)):
                os.link(staged, final)
                st = final.stat()
                created.append((final, st.st_dev, st.st_ino))
        except BaseException:
            for path, dev, ino in reversed(created):
                try:
                    st = path.lstat()
                    if (st.st_dev, st.st_ino) == (dev, ino):
                        path.unlink()
                except FileNotFoundError:
                    pass
            raise
    print(f'已保留 {seconds:.3f} 秒 / {nframes} 帧（30 fps）：{video_out}')
    print(f'已提取实际保留末帧：{tail_out}')
    print(f'已另存下一段离线请求：{tasks_out}（{next_id}）；请实际附图提交 Muse。')
    print(f'后续使用原片 assemble 时，对上一段指定 --keep-frames {previous_id}={nframes}，并复核最终剪点。')
    print('仅图片参考，不保证首帧硬锁；表情、台词、音频和接点需实际审看。')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        detail = error.stderr.decode(errors='replace') if isinstance(getattr(error, 'stderr', None), bytes) else str(error)
        sys.exit(f'尾帧接力准备失败：{detail}')
