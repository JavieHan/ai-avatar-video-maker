#!/usr/bin/env python3
"""Import actual Muse MP4 exports into a local clips.json; never calls Muse or a network API."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from muse_common import local_file, probe_video, read_json, segment_id, task_hash, write_json


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tasks", type=Path)
    parser.add_argument("results", type=Path, help='实际下载结果：{"s1":{"src":"下载的.mp4","source_url":"Muse会话URL"}}')
    parser.add_argument("output", type=Path, help="本地 clips.json，可逐批追加")
    parser.add_argument("--replace", action="store_true", help="允许更新已有片段的清单记录，原始文件不覆盖")
    args = parser.parse_args()
    request = read_json(args.tasks)
    if not isinstance(request, dict) or request.get("provider") != "muse" or not isinstance(request.get("tasks"), list) or not request["tasks"]:
        raise ValueError("tasks.json 不是非空 Muse 请求清单")
    ids = [segment_id(item.get("id")) for item in request["tasks"]]
    if len(set(ids)) != len(ids):
        raise ValueError("tasks.json 中片段 id 重复")
    results = read_json(args.results)
    if not isinstance(results, dict) or not results:
        raise ValueError("results.json 必须是非空的实际下载结果映射")
    output = args.output.resolve()
    existing = read_json(output) if output.exists() else {}
    if not isinstance(existing, dict):
        raise ValueError("已有 clips.json 必须是对象")
    task_map = {item["id"]: item for item in request["tasks"]}
    for sid, entry in existing.items():
        segment_id(sid)
        if not isinstance(entry, dict) or entry.get("provider") != "muse" or entry.get("review_status") not in {"pending", "approved", "rejected"}:
            raise ValueError(f"已有 {sid} 不是有效的 Muse 片段记录")
        if sid not in task_map or entry.get("request_sha256") != task_hash(task_map[sid]):
            entry["request_status"] = "stale"
            entry["review_status"] = "pending"
        elif not (sid in results and args.replace):
            try:
                local_file(entry.get("src"), output.parent)
            except ValueError:
                entry["request_status"] = "missing_file"
                entry["review_status"] = "pending"
    prepared = []
    for sid, item in results.items():
        segment_id(sid)
        if sid not in ids:
            raise ValueError(f"结果 {sid} 不在请求清单中")
        item = {"src": item} if isinstance(item, str) else item
        if not isinstance(item, dict):
            raise ValueError(f"{sid} 的结果必须是本地路径或对象")
        source = local_file(item.get("src"), args.results.resolve().parent)
        if source.suffix.lower() != ".mp4":
            raise ValueError(f"{sid} 请先从 Muse 导出 MP4，或在本地单独转为 MP4")
        info = probe_video(source)
        subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(source), "-f", "null", "-"],
                       check=True, capture_output=True)
        checksum = digest(source)
        if sid in existing and existing[sid].get("sha256") != checksum and not args.replace:
            raise ValueError(f"{sid} 已有不同片段；确需替换时显式加 --replace，旧视频不会被覆盖")
        target = output.parent / "gen" / f"{sid}-{checksum[:12]}.mp4"
        if target.exists() and digest(target) != checksum:
            raise ValueError(f"目标文件存在且内容不同：{target}")
        if item.get("source_url") is not None and not isinstance(item["source_url"], str):
            raise ValueError(f"{sid} 的 source_url 必须是实际 URL 字符串或 null")
        if item.get("model") is not None and not isinstance(item["model"], str):
            raise ValueError(f"{sid} 的 model 必须是实际披露的名称或 null")
        request_hash = task_hash(task_map[sid])
        prepared.append((sid, source, target, checksum, info, item, request_hash))
    output.parent.mkdir(parents=True, exist_ok=True)
    for sid, source, target, checksum, info, item, request_hash in prepared:
        target.parent.mkdir(parents=True, exist_ok=True)
        if source != target and not target.exists():
            shutil.copy2(source, target)
        old = existing.get(sid, {})
        unchanged = old.get("sha256") == checksum and old.get("request_sha256") == request_hash
        existing[sid] = {"src": os.path.relpath(target, output.parent), "provider": "muse",
                         "source_url": item.get("source_url", old.get("source_url") if unchanged else None),
                         "model": item.get("model", old.get("model") if unchanged else None),
                         "sha256": checksum, "request_sha256": request_hash, "probe": info,
                         "request_status": "matched",
                         "review_status": old.get("review_status", "pending") if unchanged else "pending"}
    write_json(output, existing)
    missing = sorted(sid for sid in ids if existing.get(sid, {}).get("request_status") != "matched")
    print(f"已导入 {len(prepared)} 段实际视频，清单 {output}；内容、台词和口型仍需审看。")
    if missing:
        print("尚未有效导入（缺片、源文件缺失或请求已改变）：" + ", ".join(missing))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        detail = error.stderr.decode(errors="replace") if isinstance(getattr(error, "stderr", None), bytes) else str(error)
        sys.exit(f"导入失败：{detail}")
