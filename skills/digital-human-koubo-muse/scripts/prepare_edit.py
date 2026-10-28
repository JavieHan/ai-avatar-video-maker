#!/usr/bin/env python3
"""Prepare a clean, editable Remotion talking-head project from user-owned media.

No generation, downloading, transcription, speech alignment, or rendering is done.
Supplying --voice replaces the existing audio track in the edit; it does not drive
lip movement. Align the replacement audio and timeline to the video before use.
"""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def probe(path):
    completed = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                                '-of', 'json', str(path)], check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def media_file(path):
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise ValueError(f'找不到文件：{p}')
    return p


def video_info(path):
    info = probe(path)
    video = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), None)
    if not video:
        raise ValueError('主视频没有视频轨')
    audio = any(s.get('codec_type') == 'audio' for s in info.get('streams', []))
    width, height = int(video['width']), int(video['height'])
    rotation = video.get('tags', {}).get('rotate', 0)
    for side in video.get('side_data_list', []):
        if 'rotation' in side:
            rotation = side['rotation']
            break
    try:
        if abs(float(rotation)) % 180 == 90:
            width, height = height, width
    except (TypeError, ValueError):
        pass
    try:
        duration = float(video.get('duration', 'nan'))
    except (TypeError, ValueError):
        duration = float('nan')
    if not math.isfinite(duration) or duration <= 0:
        duration = float(info.get('format', {}).get('duration', 0))
    if width < 2 or height < 2 or not math.isfinite(duration) or duration <= 0:
        raise ValueError('无法读取主视频尺寸或时长')
    return width, height, duration, audio


def audio_file(path):
    p=media_file(path)
    if p.suffix.lower() not in ('.wav', '.mp3', '.m4a', '.aac', '.flac', '.ogg'):
        raise ValueError(f'不支持的音频格式：{p.suffix}')
    info=probe(p)
    if not any(s.get('codec_type') == 'audio' for s in info.get('streams', [])):
        raise ValueError(f'音频文件无有效音轨：{p}')
    return p


def finite_number(value):
    return isinstance(value, (int,float)) and not isinstance(value,bool) and math.isfinite(value)


def timeline_file(path, video_duration):
    p=media_file(path)
    value=json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(value,dict) or not finite_number(value.get('total')) or value['total'] <= 0:
        raise ValueError('时间轴必须包含正数 total 和非空 segs')
    if value['total'] > video_duration + .15:
        raise ValueError(f"字幕时间轴 {value['total']:.2f}s 超过视频 {video_duration:.2f}s")
    segs=value.get('segs')
    if not isinstance(segs,list) or not segs:
        raise ValueError('时间轴 segs 必须为非空数组')
    previous=0
    for n,segment in enumerate(segs,1):
        if not isinstance(segment,dict) or not isinstance(segment.get('text'),str) or not segment['text'].strip():
            raise ValueError(f'字幕第 {n} 段缺少文字')
        start,end=segment.get('start'),segment.get('end')
        if not finite_number(start) or not finite_number(end) or start < 0 or start < previous-.04 or end<=start or end>video_duration+.15 or end>value['total']+.15:
            raise ValueError(f'字幕第 {n} 段时间无效或超出视频')
        if 'chars' in segment and not isinstance(segment['chars'],dict):
            raise ValueError(f'字幕第 {n} 段 chars 必须是对象')
        previous=end
    return p,value


def sticker_data(path, duration):
    if not path:
        return []
    p=media_file(path)
    rows=json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(rows,list):
        raise ValueError('贴纸文件应为数组')
    for n,row in enumerate(rows,1):
        if not isinstance(row,dict):
            raise ValueError(f'贴纸 {n} 应为对象')
        start,end=row.get('start'),row.get('end')
        if not finite_number(start) or not finite_number(end) or not 0<=start<end<=duration:
            raise ValueError(f'贴纸 {n} 时间无效或超出视频')
        if not isinstance(row.get('title'),str) or not row['title'].strip() or len(row['title'])>25:
            raise ValueError(f'贴纸 {n} 的 title 需为 1 至 25 字')
        tags=row.get('tags',[])
        if not isinstance(tags,list) or len(tags)>3 or any(not isinstance(x,str) or not x.strip() or len(x)>8 for x in tags):
            raise ValueError(f'贴纸 {n} 的 tags 至多三项，每项 1 至 8 字')
        row['tags']=tags
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',required=True,help='本地完整口播 MP4，必须为你有权使用的媒体')
    parser.add_argument('--timeline',required=True,help='已核对的 tl.json（时间基准与主视频相同）')
    parser.add_argument('--output',required=True,help='新建工程目录，已有目录不会被覆盖')
    parser.add_argument('--voice',help='可选：已与主视频对齐的替换音轨；后期配音，不驱动口型')
    parser.add_argument('--music',help='可选：已获授权的背景音乐')
    parser.add_argument('--music-volume',type=float,default=.12,help='背景音乐音量倍数（默认 0.12）')
    parser.add_argument('--stickers',help='可选 JSON 数组，项目文字和秒数由用户提供')
    parser.add_argument('--badge',help='可选的简短画面标签，未指定时不添加')
    args=parser.parse_args()
    video=media_file(args.video)
    if video.suffix.lower()!='.mp4':
        raise ValueError('主视频请使用 MP4 格式')
    width,height,duration,has_audio=video_info(video)
    timeline,_=timeline_file(args.timeline,duration)
    voice=audio_file(args.voice) if args.voice else None
    music=audio_file(args.music) if args.music else None
    if not has_audio and not voice:
        raise ValueError('主视频没有音轨；请提供已对齐的 --voice')
    if not math.isfinite(args.music_volume) or not 0<=args.music_volume<=1:
        raise ValueError('--music-volume 必须介于 0 和 1')
    if args.badge is not None and len(args.badge)>40:
        raise ValueError('--badge 最多 40 字')
    stickers=sticker_data(args.stickers,duration)
    target=Path(args.output).expanduser().absolute()
    if target.exists() or target.is_symlink():
        raise ValueError(f'目标工程已存在，不覆盖：{target}')
    if not target.parent.is_dir():
        raise ValueError(f'目标的父目录不存在：{target.parent}')
    template=Path(__file__).resolve().parent.parent/'templates'/'huazi-916'
    if not template.is_dir():
        raise ValueError(f'找不到基础模板：{template}')
    # All files are staged before reserving the destination. The source project is never changed.
    stage=Path(tempfile.mkdtemp(prefix='.koubo-edit-',dir=target.parent))
    reserved=False
    try:
        shutil.copytree(template,stage,dirs_exist_ok=True,ignore=shutil.ignore_patterns('node_modules','.DS_Store'))
        pub=stage/'public'
        shutil.copy2(video,pub/'main.mp4')
        shutil.copy2(timeline,stage/'src'/'tl.json')
        names={}
        for key,item in [('voice',voice),('music',music)]:
            names[key]=f'{key}{item.suffix.lower()}' if item else None
            if item:
                shutil.copy2(item,pub/names[key])
        # H.264 requires even dimensions; a one-pixel letterbox keeps all source pixels visible.
        config={'width':width+width%2,'height':height+height%2,'fps':30,'duration':duration,
                'video':'main.mp4','voice':names['voice'],'music':names['music'],
                'musicVolume':args.music_volume,'badge':args.badge or None,'stickers':stickers}
        (stage/'src'/'edit.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        os.mkdir(target)
        reserved=True
        os.replace(stage,target)
    except BaseException:
        if reserved:
            try: target.rmdir()
            except OSError: pass
        if stage.exists(): shutil.rmtree(stage)
        raise
    print(f'已创建：{target}')
    print(f'画布 {config["width"]}×{config["height"]}，30fps，{duration:.2f}s；画面按比例完整显示。')
    print('音频：' + ('外部配音（后期替换，不驱动口型）' if voice else '主视频原音'))
    print('请在工程目录运行 npm install，然后 bash scripts/render.sh ../成片.mp4。')
    print('字幕和口型需实际审看；请勿覆盖原视频或既有成片。')

if __name__ == '__main__':
    try: main()
    except (ValueError,OSError,subprocess.CalledProcessError,json.JSONDecodeError) as e:
        detail=e.stderr if isinstance(getattr(e,'stderr',None),str) and e.stderr else str(e)
        sys.exit(f'准备失败：{detail}')
