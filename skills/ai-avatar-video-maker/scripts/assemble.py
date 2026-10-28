#!/usr/bin/env python3
"""Muse local clips -> Whisper script check -> synchronized tail trim -> MP4.

Usage: assemble.py script.json clips.json --out final.mp4 [--cut-dir cut]
clips.json is written by import_muse.py; paths are relative to that manifest.
Whisper matching is automated evidence, not a listening or lip-sync approval.
"""
import argparse
import difflib
import os
from pathlib import Path
import re
import subprocess
import sys

from muse_common import clip_entry, file_hash, load_script, probe_video, read_json, task_hash, write_json


def run(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def model_path(explicit):
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise ValueError(f"Whisper 模型不存在：{path}")
        return path
    for value in ["~/models/ggml-medium-q5_0.bin", "~/.cache/whisper/ggml-medium-q5_0.bin",
                  "~/Library/Application Support/Murmur/models/ggml-medium-q5_0.bin", "~/models/ggml-medium.bin"]:
        path = Path(value).expanduser()
        if path.is_file():
            return path
    raise ValueError("缺 Whisper 模型；请设置 WHISPER_MODEL 或使用 --model 指定现有模型，不会自动下载")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path)
    parser.add_argument("clips", type=Path)
    parser.add_argument("--tasks", type=Path, help="当前 Muse 请求，默认读取 clips.json 同目录的 tasks.json")
    parser.add_argument("--out", type=Path, default=Path("成片_完整版.mp4"))
    parser.add_argument("--cut-dir", type=Path, default=Path("cut"))
    parser.add_argument("--lang", default="zh")
    parser.add_argument("--size", help="统一输出尺寸，例如 720x1280；不同画幅用等比缩放和补边")
    parser.add_argument("--model", default=os.environ.get("WHISPER_MODEL"))
    parser.add_argument("--whisper-cli", default="whisper-cli")
    parser.add_argument("--keep-frames", action="append", default=[], metavar="ID=COUNT", help="已选定续接尾帧时，明确保留该段的30fps输出帧数；仍识别完整原片")
    parser.add_argument("--accept-asr-mismatch", action="append", default=[], metavar="ID", help="实际复核后逐段确认 ASR 数字/读法误差，可重复指定")
    parser.add_argument("--accept-spoken-error", action="append", default=[], metavar="ID", help="实际听到原生语音错误并计划后期换声，可逐段明确记录")
    parser.add_argument("--review-note", help="上述识别误差或原生语音错误的实际复核依据，不代表口型通过")
    parser.add_argument("--allow-pending", action="store_true", help="仅供预览：允许未人工审核的片段；拒绝的片段仍不会拼接")
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError(f"输出已存在，未覆盖：{args.out}")
    if args.cut_dir.exists() and any(args.cut_dir.iterdir()):
        raise ValueError(f"中间目录非空，未覆盖：{args.cut_dir}；请用 --cut-dir 指定新的目录")
    script = load_script(args.script)
    manifest = read_json(args.clips)
    if not isinstance(manifest, dict):
        raise ValueError("clips.json 必须是本地 Muse 片段映射")
    requests = read_json(args.tasks or args.clips.resolve().parent / "tasks.json")
    if not isinstance(requests, dict) or requests.get("provider") != "muse" or not isinstance(requests.get("tasks"), list):
        raise ValueError("需要当前有效的 Muse tasks.json")
    task_map = {item["id"]: item for item in requests["tasks"]}
    if len(task_map) != len(requests["tasks"]) or set(task_map) != {item["id"] for item in script}:
        raise ValueError("当前请求段号与剧本不一致，请重新准备请求")
    keep_frames = {}
    for value in args.keep_frames:
        sid, separator, count = value.partition("=")
        if not separator or sid not in task_map or not count.isdigit() or int(count) < 1 or sid in keep_frames:
            raise ValueError("--keep-frames 需要不重复的有效段号=正整数帧数")
        keep_frames[sid] = int(count)
    accepted = set(args.accept_asr_mismatch)
    spoken_errors = set(args.accept_spoken_error)
    if (not (accepted | spoken_errors).issubset(task_map) or accepted & spoken_errors or
            ((accepted or spoken_errors) and not (args.review_note or "").strip())):
        raise ValueError("复核须指定不同的有效片段 ID，并用 --review-note 记录实际依据")
    sources = []
    for item in script:
        source, entry = clip_entry(manifest, item["id"], args.clips.resolve().parent)
        if entry.get("review_status") != "approved" and not args.allow_pending:
            raise ValueError(f"{item['id']} 尚未人工审核通过；预览可指定 --allow-pending")
        if args.out.resolve() == source.resolve():
            raise ValueError(f"输出不能覆盖原视频：{source}")
        if task_map[item["id"]].get("script") != item["t"] or entry.get("request_sha256") != task_hash(task_map[item["id"]]):
            raise ValueError(f"{item['id']} 的剧本、人物或声音请求已改变，请重新准备/导入并复核")
        if entry.get("sha256") != file_hash(source):
            raise ValueError(f"{item['id']} 导入后的视频内容已改变，请重新导入与复核")
        sources.append((source, entry, probe_video(source)))
    if args.size:
        if not re.fullmatch(r"[1-9][0-9]*x[1-9][0-9]*", args.size):
            raise ValueError("--size 需要 宽x高，例如 720x1280")
        width, height = map(int, args.size.split("x"))
        if width % 2 or height % 2:
            raise ValueError("输出宽高必须为偶数")
    else:
        dimensions = {(info["width"], info["height"]) for _, _, info in sources}
        if len(dimensions) != 1:
            raise ValueError("片段尺寸不同；请明确 --size，工具将等比缩放补边，不会拉伸人像")
        width, height = next(iter(dimensions))
        width -= width % 2
        height -= height % 2
    model = model_path(args.model)
    cuts = args.cut_dir.resolve()
    cuts.mkdir(parents=True, exist_ok=True)
    reports = []
    clean = lambda value: re.sub(r"[\s，。、：；！？,.:;!?“”]", "", value).lower()
    for item, (source, entry, info) in zip(script, sources):
        sid = item["id"]
        wav, transcript = cuts / f"{sid}.wav", cuts / f"{sid}.json"
        language = item.get("lang_code", args.lang)
        run(["ffmpeg", "-v", "error", "-n", "-i", str(source), "-vn", "-ar", "16000", "-ac", "1", str(wav)])
        try:
            command = [args.whisper_cli, "-m", str(model), "-l", language]
            if language == "zh":
                command += ["--prompt", "以下是普通话的句子。", "-ml", "1"]
            command += ["-oj", "-of", str(cuts / sid), "-f", str(wav)]
            run(command, capture_output=True)
            rows = [row for row in read_json(transcript)["transcription"]
                    if row.get("text", "").strip() and not row["text"].strip().startswith("[")]
            if not rows:
                raise ValueError(f"{sid} 未识别到语音，暂停合成；检查实际台词和转写结果")
            heard = "".join(row["text"] for row in rows)
            # Punctuation may inherit the decoder's padded 30-second boundary.
            # It is not spoken audio and must not determine the cut point.
            spoken_rows = [row for row in rows if any(ch.isalnum() for ch in row["text"])]
            if not spoken_rows:
                raise ValueError(f"{sid} 未识别到有效语音字符")
            start = min(row["offsets"]["from"] for row in spoken_rows) / 1000
            end = max(row["offsets"]["to"] for row in spoken_rows) / 1000
            if not 0 <= start < end <= info["duration"] + 0.25:
                raise ValueError(f"{sid} 语音时间戳超出视频范围，暂停合成")
            keep = min(info["duration"], end + 0.25)
            if sid in keep_frames:
                keep = keep_frames[sid] / 30
                if keep < end or keep > info["duration"] + 1 / 30:
                    raise ValueError(f"{sid} 指定保留帧数会截断已识别台词或超出原片")
            accuracy = difflib.SequenceMatcher(None, clean(item["t"]), clean(heard), autojunk=False).ratio()
            video_filter = (f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p")
            run(["ffmpeg", "-v", "error", "-n", "-i", str(source), "-t", f"{keep:.3f}",
                 "-vf", video_filter, "-af", "aresample=48000",
                 *(["-frames:v", str(keep_frames[sid])] if sid in keep_frames else []),
                 "-ac", "2", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-c:a", "aac",
                 "-b:a", "192k", str(cuts / f"{sid}.mp4")])
            reports.append({"id": sid, "provider": "muse", "src": str(source), "acc": round(accuracy, 3),
                            "speech": [round(start, 2), round(end, 2)], "keep": round(keep, 3),
                            "explicit_keep_frames": keep_frames.get(sid),
                            "src_dur": info["duration"], "heard": heard, "review_status": entry["review_status"],
                            "script_similarity_below_threshold": accuracy < 0.85,
                            "script_review_required": accuracy < 0.85 and sid not in (accepted | spoken_errors),
                            "asr_mismatch_accepted": sid in accepted,
                            "asr_review_note": args.review_note if sid in accepted else None,
                            "spoken_error_accepted_for_redub": sid in spoken_errors,
                            "spoken_error_note": args.review_note if sid in spoken_errors else None,
                            "lip_sync_verified": False})
            print(f"{sid}: 转写相似度 {accuracy:.0%}，保留 {keep:.2f}s；口型需审看" + ("，台词需复核" if accuracy < 0.85 else ""))
        finally:
            wav.unlink(missing_ok=True)
    write_json(cuts / "qa.json", reports)
    if any(row["script_review_required"] for row in reports):
        raise ValueError(f"存在转写相似度低于 85% 的片段；已保存 {cuts / 'qa.json'}。先复核台词；如确认 ASR 误差或实际口播错误并计划换声，分别用 --accept-asr-mismatch / --accept-spoken-error 加 --review-note 记录，不自动重拍")
    listing = cuts / "list.txt"
    joined = cuts / "joined.mp4"
    listing.write_text("".join(f"file '{item['id']}.mp4'\n" for item in script), encoding="utf-8")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    try:
        run(["ffmpeg", "-v", "error", "-n", "-f", "concat", "-safe", "0", "-i", str(listing),
             "-c", "copy", str(joined)])
        run(["ffmpeg", "-v", "error", "-n", "-i", str(joined), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(args.out)])
    finally:
        joined.unlink(missing_ok=True)
        listing.unlink(missing_ok=True)
    print(f"拼接完成：{args.out}；这是本地处理结果，未代表台词、口型或声音已通过人工验收。")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        detail = error.stderr.decode(errors="replace") if isinstance(getattr(error, "stderr", None), bytes) else str(error)
        sys.exit(f"合成暂停：{detail}")
