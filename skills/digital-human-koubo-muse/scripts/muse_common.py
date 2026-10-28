"""Local file contracts for the Muse UI workflow. No network or generation calls."""
import json
import hashlib
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"JSON 键重复：{key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique)


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=".muse-", delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def task_hash(task):
    # A reference path alone is not a stable identity: the file may be replaced.
    expected = task.get("reference_image_sha256")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("请求缺少参考图 SHA256，请重新运行 build_tasks.py 或 handoff.py")
    path = local_file(task.get("reference_image"), Path.cwd())
    if file_hash(path) != expected:
        raise ValueError(f"参考图内容已更改：{path}；请重新准备请求及复核素材")
    return hashlib.sha256(json.dumps(task, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def file_hash(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def segment_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value):
        raise ValueError(f"片段 id 必须是 1–80 位字母、数字、下划线或连字符：{value!r}")
    return value


def load_script(path):
    script = read_json(path)
    if not isinstance(script, list) or not script:
        raise ValueError("script.json 必须是非空片段数组")
    seen = set()
    for item in script:
        if not isinstance(item, dict):
            raise ValueError("每个片段必须是对象")
        sid = segment_id(item.get("id"))
        if sid in seen:
            raise ValueError(f"片段 id 重复：{sid}")
        seen.add(sid)
        if not isinstance(item.get("t"), str) or not item["t"].strip():
            raise ValueError(f"{sid} 缺少非空台词 t")
    return script


def local_file(value, base):
    if not isinstance(value, str) or not value.strip() or "://" in value:
        raise ValueError("需要本地文件路径，不能使用 task/material 编号或远程 URL")
    path = Path(value).expanduser()
    path = (Path(base) / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_file():
        raise ValueError(f"本地文件不存在：{path}")
    return path


def probe_video(path, require_audio=True):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                             "-of", "json", str(path)], check=True, capture_output=True, text=True)
    info = json.loads(result.stdout)
    video = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    audio = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    duration = float(info.get("format", {}).get("duration", 0))
    if not video or not math.isfinite(duration) or duration <= 0:
        raise ValueError(f"不是有效的视频文件：{path}")
    if require_audio and not audio:
        raise ValueError(f"口播片段没有音轨：{path}。请核实 Muse 是否实际生成了台词和口型，不能用静音片冒充口播。")
    return {"duration": duration, "width": video["width"], "height": video["height"], "has_audio": audio}


def clip_entry(manifest, sid, base, allow_rejected=False, require_current=True):
    item = manifest.get(sid)
    if not isinstance(item, dict) or item.get("provider") != "muse":
        raise ValueError(f"{sid} 缺少 Muse 本地片段记录；先运行 import_muse.py")
    statuses = {"pending", "approved", "rejected"} if allow_rejected else {"pending", "approved"}
    if item.get("review_status") not in statuses:
        raise ValueError(f"{sid} 未审状态不合法或片段已被拒绝")
    if require_current and item.get("request_status") != "matched":
        raise ValueError(f"{sid} 不是当前请求的有效导入结果，请重新导入该段实际视频")
    return local_file(item.get("src"), base), item
