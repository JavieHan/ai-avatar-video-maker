"""End-to-end checks of no-clobber handoff and source frame / audio preservation."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills' / 'ai-avatar-video-maker' / 'scripts'
sys.path.insert(0, str(SCRIPTS))
from muse_common import file_hash, task_hash


def run(*args, ok=True):
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True)
    if ok and result.returncode:
        raise AssertionError(result.stderr)
    return result


class HandoffTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.p = Path(self.temp.name)
        self.video = self.p / 'input.mp4'
        run('ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=96x160:rate=24:duration=2',
            '-f', 'lavfi', '-i', 'sine=frequency=700:sample_rate=48000:duration=2',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', self.video)
        self.ref = self.p / 'person.png'
        run('ffmpeg', '-v', 'error', '-i', self.video, '-frames:v', '1', self.ref)
        (self.p / 'persona.json').write_text(json.dumps({'reference_image': str(self.ref),
            'voice': {'description': '自然声音'}, 'generation': {'provider': 'muse'}}))
        (self.p / 'script.json').write_text(json.dumps([{'id': 's1', 't': '第一句', 'duration': 2},
                                                        {'id': 's2', 't': '第二句', 'duration': 2}]))
        self.tasks = self.p / 'tasks.json'
        run(sys.executable, SCRIPTS / 'build_tasks.py', self.p / 'script.json', self.tasks,
            '--persona', self.p / 'persona.json')

    def tearDown(self):
        self.temp.cleanup()

    def handoff(self, **overrides):
        o = {'video': self.video, 'keep_seconds': '1.2', 'trimmed': self.p / 'cut.mp4',
             'tail': self.p / 'tail.png', 'tasks': self.tasks, 'next_id': 's2',
             'output_tasks': self.p / 'next.json'}
        o.update(overrides)
        return run(sys.executable, SCRIPTS / 'handoff.py', *sum(([f'--{k.replace("_", "-")}', v] for k, v in o.items()), []), ok=False)

    def test_actual_final_frame_audio_and_tasks(self):
        result = self.handoff()
        self.assertEqual(result.returncode, 0, result.stderr)
        trimmed, tail = self.p / 'cut.mp4', self.p / 'tail.png'
        probe = json.loads(run('ffprobe', '-v', 'error', '-count_frames', '-show_entries',
            'stream=codec_type,nb_read_frames,duration', '-of', 'json', trimmed).stdout)
        video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        audio = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
        self.assertEqual(int(video['nb_read_frames']), 36)
        self.assertGreater(float(audio['duration']), 1.1)
        # Both pixel streams are decoded the same way; the PNG must be exactly
        # the actual last video frame, not merely the frame at a timestamp guess.
        a = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(trimmed), '-vf',
            'select=eq(n\\,35)', '-frames:v', '1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
        b = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(tail), '-frames:v', '1',
            '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'])
        self.assertEqual(a, b)
        original = json.loads(self.tasks.read_text())
        new = json.loads((self.p / 'next.json').read_text())
        self.assertEqual(original['tasks'][0], new['tasks'][0])
        next_task = new['tasks'][1]
        self.assertEqual(Path(next_task['reference_image']), tail.resolve())
        self.assertEqual(next_task['reference_image_sha256'], file_hash(tail))
        self.assertEqual(next_task['handoff']['retained_frames'], 36)
        self.assertFalse(next_task['handoff']['first_frame_locked'])
        self.assertEqual(next_task['status'], 'prepared_not_generated')
        task_hash(next_task)
        tail.write_bytes(b'replaced image')
        with self.assertRaisesRegex(ValueError, '参考图内容已更改'):
            task_hash(next_task)

    def test_existing_output_does_not_overwrite_anything(self):
        existing = self.p / 'tail.png'
        existing.write_bytes(b'keep me')
        r = self.handoff()
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(existing.read_bytes(), b'keep me')
        self.assertFalse((self.p / 'cut.mp4').exists())
        self.assertFalse((self.p / 'next.json').exists())

    def test_dangling_output_symlink_does_not_create_target(self):
        link = self.p / 'tail.png'
        target = self.p / 'do-not-create.png'
        link.symlink_to(target)
        r = self.handoff()
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(link.is_symlink())
        self.assertFalse(target.exists())
        self.assertFalse((self.p / 'cut.mp4').exists())

    def test_invalid_duration_does_not_create_outputs(self):
        r = self.handoff(keep_seconds='9')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.p / 'cut.mp4').exists())
        self.assertFalse((self.p / 'tail.png').exists())
        self.assertFalse((self.p / 'next.json').exists())

    def test_import_and_assemble_reject_changed_reference(self):
        result_file = self.p / 'results.json'
        result_file.write_text(json.dumps({'s1': {'src': str(self.video)}}))
        clips = self.p / 'clips.json'
        imported = run(sys.executable, SCRIPTS / 'import_muse.py', self.tasks, result_file, clips, ok=False)
        self.assertEqual(imported.returncode, 0, imported.stderr)
        self.ref.write_bytes(b'changed')
        rejected = run(sys.executable, SCRIPTS / 'import_muse.py', self.tasks, result_file, clips, ok=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn('参考图内容已更改', rejected.stderr)
        assembled = run(sys.executable, SCRIPTS / 'assemble.py', self.p / 'script.json', clips,
                        '--out', self.p / 'final.mp4', '--allow-pending', ok=False)
        self.assertNotEqual(assembled.returncode, 0)
        self.assertIn('参考图内容已更改', assembled.stderr)
        self.assertFalse((self.p / 'final.mp4').exists())

    def test_image_mutation_invalidates_original_request(self):
        task = json.loads(self.tasks.read_text())['tasks'][0]
        task_hash(task)
        self.ref.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, '参考图内容已更改'):
            task_hash(task)


if __name__ == '__main__':
    unittest.main()
