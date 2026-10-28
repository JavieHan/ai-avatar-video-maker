"""Checkout-local registration and read-only dependency checks; no agent clients used."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = "ai-avatar-video-maker"


def snapshot(root):
    """Include link destinations, file bytes and mtimes without following links."""
    result = {}
    for directory, directories, files in os.walk(root):
        for name in directories + files:
            path = Path(directory) / name
            kind = "link" if path.is_symlink() else "dir" if path.is_dir() else "file"
            content = os.readlink(path) if kind == "link" else path.read_bytes() if kind == "file" else None
            result[str(path.relative_to(root))] = (kind, content, path.lstat().st_mtime_ns)
    return result


class AgentSetupTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agent setup ")
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base / "checkout with spaces"
        self.repo.mkdir()
        for relative in ("setup.sh", "scripts/configure_agent.py",
                         f"skills/{SKILL}/SKILL.md", f"skills/{SKILL}/scripts/doctor.sh"):
            destination = self.repo / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        self.bin = self.base / "tool stubs"
        self.bin.mkdir()
        for name, executable in (("python3", sys.executable), ("sh", "/bin/sh"),
                                 ("dirname", "/usr/bin/dirname")):
            (self.bin / name).symlink_to(executable)
        for name in ("ffmpeg", "ffprobe", "npm", "whisper-cli"):
            self.executable(name, "exit 0\n")
        self.executable("node", "printf '%s\\n' 'v22.12.0'\n")
        self.model = self.base / "local model.bin"
        self.model.write_bytes(b"fixture model, never loaded")
        self.home = self.base / "untouched home"
        self.home.mkdir()
        (self.home / ".claude").mkdir()
        (self.home / ".claude" / "settings.json").write_text('{"keep": true}')
        self.home_before = snapshot(self.home)
        self.env = dict(os.environ, PATH=str(self.bin), HOME=str(self.home), WHISPER_MODEL=str(self.model))

    def tearDown(self):
        try:
            self.assertEqual(snapshot(self.home), self.home_before, "setup changed global configuration")
        finally:
            self.temp.cleanup()

    def executable(self, name, body):
        path = self.bin / name
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(0o755)

    def setup(self, *args):
        return subprocess.run(["/bin/bash", str(self.repo / "setup.sh"), *args], cwd=self.base,
                              env=self.env, capture_output=True, text=True)

    def link(self, agent):
        return self.repo / (".agents" if agent == "codex" else ".claude") / "skills" / SKILL

    def assert_link(self, agent):
        link = self.link(agent)
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.readlink(link), f"../../skills/{SKILL}")
        self.assertEqual(link.resolve(), self.repo / "skills" / SKILL)

    def test_default_both_and_paths_with_spaces(self):
        result = self.setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_link("codex")
        self.assert_link("claude")
        self.assertIn("环境依赖检查通过", result.stdout)

    def test_individual_agent_only(self):
        for agent, other in (("codex", "claude"), ("claude", "codex")):
            with self.subTest(agent=agent):
                result = self.setup(agent)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assert_link(agent)
                self.assertFalse(self.link(other).exists())
                shutil.rmtree(self.link(agent).parent.parent)

    def test_rerun_preserves_links_and_unrelated_config(self):
        for name in (".agents", ".claude"):
            (self.repo / name).mkdir()
            (self.repo / name / "settings.json").write_text('{"custom": true}')
        self.assertEqual(self.setup("both").returncode, 0)
        before = snapshot(self.repo)
        result = self.setup("both")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.repo), before)

    def test_second_target_conflict_changes_nothing(self):
        self.link("claude").parent.mkdir(parents=True)
        self.link("claude").write_text("existing user config")
        before = snapshot(self.repo)
        result = self.setup("both")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("已有同名配置", result.stderr)
        self.assertEqual(snapshot(self.repo), before)
        self.assertFalse((self.repo / ".agents").exists())

    def test_directory_and_wrong_or_dangling_link_conflicts(self):
        self.link("claude").parent.mkdir(parents=True)
        for kind in ("directory", "wrong_link", "dangling_link", "symlink_loop"):
            with self.subTest(kind=kind):
                target = self.link("claude")
                if kind == "directory":
                    target.mkdir()
                elif kind == "wrong_link":
                    target.symlink_to(self.home, target_is_directory=True)
                elif kind == "symlink_loop":
                    target.symlink_to(target.name, target_is_directory=True)
                else:
                    target.symlink_to(self.base / "does not exist", target_is_directory=True)
                before = snapshot(self.repo)
                self.assertEqual(self.setup("both").returncode, 1)
                self.assertEqual(snapshot(self.repo), before)
                target.rmdir() if kind == "directory" else target.unlink()

    def test_external_parent_symlinks_are_not_followed(self):
        for relative in (".claude", ".claude/skills"):
            with self.subTest(parent=relative):
                parent = self.repo / relative
                parent.parent.mkdir(parents=True, exist_ok=True)
                parent.symlink_to(self.home, target_is_directory=True)
                before = snapshot(self.repo)
                result = self.setup("both")
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertEqual(snapshot(self.repo), before)
                self.assertFalse((self.home / SKILL).exists())
                self.assertFalse((self.home / "skills").exists())
                parent.unlink()

    def test_parent_file_conflict_changes_nothing(self):
        (self.repo / ".claude").write_text("keep")
        before = snapshot(self.repo)
        self.assertEqual(self.setup("both").returncode, 1)
        self.assertEqual(snapshot(self.repo), before)

    def test_missing_model_retains_successful_registration(self):
        del self.env["WHISPER_MODEL"]
        result = self.setup()
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("WHISPER_MODEL", result.stdout)
        self.assertIn("技能已配置；环境缺依赖", result.stderr)
        self.assert_link("codex")
        self.assert_link("claude")
        before = snapshot(self.repo)
        self.assertEqual(self.setup().returncode, 3)
        self.assertEqual(snapshot(self.repo), before)

    def test_old_or_unreadable_node_version_is_not_ready(self):
        for body in ("printf '%s\\n' 'v17.9.1'\n", "exit 1\n", "printf '%s\\n' 'unknown'\n"):
            with self.subTest(node=body):
                self.executable("node", body)
                result = self.setup("codex")
                self.assertEqual(result.returncode, 3, result.stderr)
                self.assert_link("codex")
                self.assertNotIn("环境依赖检查通过", result.stdout)

    def test_missing_tool_and_nonexistent_model_are_not_ready(self):
        (self.bin / "whisper-cli").unlink()
        self.env["WHISPER_MODEL"] = str(self.base / "missing model.bin")
        result = self.setup("claude")
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("whisper-cli 未找到", result.stdout)
        self.assert_link("claude")

    def test_invalid_agent_does_not_write(self):
        before = snapshot(self.repo)
        self.assertEqual(self.setup("unknown").returncode, 2)
        self.assertEqual(snapshot(self.repo), before)


if __name__ == "__main__":
    unittest.main()
