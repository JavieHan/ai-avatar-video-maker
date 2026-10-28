import array
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/digital-human-koubo-muse/scripts/timed_voice.py'


class TimedVoiceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.p = Path(self.temp.name)
        self.video = self.p / 'input.mp4'
        self.tone = self.p / 'phrase.wav'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=gray:s=160x240:r=30:d=3',
                        '-c:v','libx264','-pix_fmt','yuv420p',str(self.video)], check=True)
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=440:duration=0.5',str(self.tone)], check=True)

    def tearDown(self):
        self.temp.cleanup()

    def run_plan(self, phrases, output='out.mp4'):
        plan = self.p / 'plan.json'
        plan.write_text(json.dumps({'phrases':phrases}), encoding='utf-8')
        result = subprocess.run(['python3', str(SCRIPT), str(self.video), str(plan), '--out', str(self.p / output)],
                                capture_output=True, text=True)
        return result, self.p / output

    def test_phrase_placement_and_no_overwrite(self):
        result, out = self.run_plan([{'audio':'phrase.wav','at':0.5}, {'audio':'phrase.wav','at':1.5}])
        self.assertEqual(result.returncode, 0, result.stderr)
        raw = subprocess.run(['ffmpeg','-v','error','-i',str(out),'-vn','-ac','1','-ar','48000',
                              '-f','s16le','-'],capture_output=True,check=True).stdout
        samples = array.array('h'); samples.frombytes(raw)
        def energy(t):
            window = samples[int(t*48000):int((t+.1)*48000)]
            return sum(abs(v) for v in window)/max(1,len(window))
        energies = [round(energy(x), 2) for x in (.2, .7, 1.2, 1.7, 2.2, 2.7)]
        print('synthetic audio seconds:', len(samples)/48000, 'window energies:', energies)
        self.assertLess(energy(.2), 50)
        self.assertGreater(energy(.7), 1000)
        self.assertLess(energy(1.2), 50)
        self.assertGreater(energy(1.7), 1000)
        original = out.read_bytes()
        again, _ = self.run_plan([{'audio':'phrase.wav','at':0.5}])
        self.assertNotEqual(again.returncode, 0)
        self.assertEqual(out.read_bytes(), original)

    def test_overlap_is_rejected(self):
        result, out = self.run_plan([{'audio':'phrase.wav','at':0.5}, {'audio':'phrase.wav','at':0.8}])
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
