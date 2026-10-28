#!/usr/bin/env python3
"""Register the canonical skill in this checkout, then check local dependencies."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


SKILL = "ai-avatar-video-maker"


def configure(root, agent):
    source = root / "skills" / SKILL
    if not (source / "SKILL.md").is_file() or root not in source.resolve().parents:
        raise ValueError("仓库内未找到有效的 canonical skill")
    doctor = source / "scripts" / "doctor.sh"
    if not doctor.is_file():
        raise ValueError("未找到依赖检查脚本 doctor.sh")

    names = ("codex", "claude") if agent == "both" else (agent,)
    targets = [root / (".agents" if name == "codex" else ".claude") / "skills" / SKILL
               for name in names]
    # Check every requested destination before creating either registration.
    # Refuse symlink parents rather than following them into another directory.
    for target in targets:
        for parent in (target.parent.parent, target.parent):
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                raise ValueError(f"配置父目录有冲突（不能是符号链接或文件）：{parent}")
        if os.path.lexists(target):
            if not target.is_symlink() or target.resolve() != source.resolve():
                raise ValueError(f"已有同名配置，保留原内容：{target}")

    created_links, created_dirs = [], []
    try:
        for target in targets:
            for parent in (target.parent.parent, target.parent):
                if not parent.exists():
                    parent.mkdir()
                    created_dirs.append(parent)
            if not target.is_symlink():
                target.symlink_to(os.path.relpath(source, target.parent), target_is_directory=True)
                created_links.append(target)
    except OSError:
        # Undo only entries created by this invocation if a filesystem write fails.
        for link in reversed(created_links):
            link.unlink()
        for directory in reversed(created_dirs):
            directory.rmdir()
        raise

    for name, target in zip(names, targets):
        print(f"技能已配置：{name} → {target.relative_to(root)}", flush=True)
    return doctor


def main():
    parser = argparse.ArgumentParser(description="在当前仓库配置 Codex / Claude Code 技能")
    parser.add_argument("agent", nargs="?", choices=("codex", "claude", "both"), default="both")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        doctor = configure(root, args.agent)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"配置失败：{error}", file=sys.stderr)
        return 1
    try:
        checked = subprocess.run(["sh", str(doctor)], cwd=root)
    except OSError as error:
        print(f"技能已配置；无法执行依赖检查：{error}；链接已保留。", file=sys.stderr)
        return 3
    if checked.returncode:
        print(f"技能已配置；环境缺依赖（doctor 退出码 {checked.returncode}），链接已保留。",
              file=sys.stderr)
        return 3
    print("技能已配置；环境依赖检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
