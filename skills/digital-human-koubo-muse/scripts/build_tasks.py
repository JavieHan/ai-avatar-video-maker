#!/usr/bin/env python3
"""Prepare Muse UI requests locally; does not submit, generate, or estimate unknown prices."""
import argparse
import math
from pathlib import Path
import re
import sys

from muse_common import file_hash, load_script, local_file, read_json, write_json


def build(script, persona, persona_base, purpose):
    if not isinstance(persona, dict):
        raise ValueError("persona.json 必须是对象")
    settings = persona.get("generation", {})
    if not isinstance(settings, dict) or settings.get("provider", "muse") != "muse":
        raise ValueError("本分支的 generation.provider 必须是 muse")
    maximum = settings.get("max_requested_seconds", 10)
    if isinstance(maximum, bool) or not isinstance(maximum, (int, float)) or not 1 <= maximum <= 60:
        raise ValueError("max_requested_seconds 必须是 1–60 的规划值；它不代表 Muse 的接口上限")
    hosts = {"main": persona, **persona.get("other_hosts", {})}
    tasks = []
    actions = {
        "full": "面向镜头，自然表情和少量手势，保持参考人物的脸、服装和机位。",
        "pip": "固定中景，平静解释，少量点头，不改变参考人物的身份与服装。",
        "vlog": "自然随和的口播，轻微头部动作，保持人物和场景一致。",
        "depth": "中景，头顶和肩膀两侧保留背景，方便后期把文字放到人物身后。",
    }
    for item in script:
        sid = item["id"]
        host_name = item.get("host", "main")
        if host_name not in hosts:
            raise ValueError(f"{sid} 未配置主播 {host_name!r}")
        host = hosts[host_name]
        if not isinstance(host, dict) or not isinstance(host.get("voice"), dict):
            raise ValueError(f"{sid} 需要主播对象和 voice.description 配置")
        reference = local_file(host.get("reference_image"), persona_base)
        voice = host.get("voice", {}).get("description")
        if not isinstance(voice, str) or not voice.strip():
            raise ValueError(f"{sid} 需要用户明确选择声音；请填写主播 voice.description，不使用作者音色或本地默认克隆音色")
        language = item.get("lang", "普通话")
        if not isinstance(language, str) or not language.strip():
            raise ValueError(f"{sid} 的 lang 必须是非空语言描述")
        shot = item.get("shot", "full")
        if shot not in actions:
            raise ValueError(f"{sid} 的 shot 需要 full / pip / vlog / depth")
        explicit = item.get("duration")
        if explicit is None:
            text = re.sub(r"[\s，。、：；！？,.:;!?“”]", "", item["t"])
            units = len(text) if re.search(r"[\u3400-\u9fff\u3040-\u30ff\uac00-\ud7af]", text) else len(item["t"].split()) * 2
            duration = max(4, math.ceil(units / 4 + 1))
        else:
            duration = explicit
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or not 1 <= duration <= maximum:
            raise ValueError(f"{sid} 请求时长 {duration!r} 秒超出本次规划的 1–{maximum} 秒，请把台词拆短；不要沿用 Grok 的时长上限")
        ratio = host.get("ratio", "9:16")
        if ratio not in {"9:16", "16:9", "1:1"}:
            raise ValueError(f"{sid} 的 ratio 需要 9:16 / 16:9 / 1:1")
        prompt = (f"制作数字人口播，用实际附上的参考图片保持同一人物。用途：{purpose}。\n"
                  f"{actions[shot]}\n语言：{language}。声音要求：{voice.strip()}。\n"
                  f"请逐字说出以下台词，并让嘴型与实际生成的声音同步：\n「{item['t']}」\n"
                  f"请求 {duration} 秒、{ratio} 构图；如当前工具不支持该时长或原生口播，请先说明，不要自行生成替代版本。\n"
                  "只保留人声和安静环境底音，不添加音乐、字幕、文字或标志。不要扩写、翻译或改写台词。")
        tasks.append({"id": sid, "host": host_name, "shot": shot, "script": item["t"],
                      "language": language, "requested_duration_seconds": duration, "ratio": ratio,
                      "reference_image": str(reference), "reference_image_sha256": file_hash(reference),
                      "requested_voice": voice.strip(), "prompt": prompt,
                      "model": None, "status": "prepared_not_generated"})
    return {"schema_version": 1, "provider": "muse", "transport": "native-ui",
            "estimated_cost": None, "speech_capability_verified": False,
            "note": "时长、声音、比例都是请求，不是已验证的 Muse 能力；由 Agent 通过实际界面提交，先确认一段再批量。",
            "tasks": tasks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--persona", type=Path, default=Path(__file__).resolve().parent.parent / "persona.json")
    parser.add_argument("--purpose", default="清晰自然地讲解用户提供的内容")
    args = parser.parse_args()
    result = build(load_script(args.script), read_json(args.persona), args.persona.resolve().parent, args.purpose)
    write_json(args.output, result)
    print(f"已准备 {len(result['tasks'])} 段 Muse 请求；未调用生成、未扣费。价格与可用能力须在实际 Muse 界面确认。")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(f"准备失败：{error}")
