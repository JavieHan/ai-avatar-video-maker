import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/digital-human-koubo-muse/scripts'


def call(*args, cwd):
    return subprocess.run([str(x) for x in args], cwd=cwd, capture_output=True, text=True)


class AssemblyWorkflowTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.p = Path(self.temp.name)
        self.video = self.p / 'a.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=gray:s=160x240:r=30:d=2',
                        '-f','lavfi','-i','sine=frequency=440:duration=2','-shortest',
                        '-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(self.video)],check=True)
        (self.p/'portrait.png').write_bytes(b'test reference image, not submitted to a model')
        (self.p/'persona.json').write_text(json.dumps({'reference_image':'portrait.png',
          'voice':{'description':'测试用音色'},'generation':{'provider':'muse'}}),encoding='utf-8')
        (self.p/'script.json').write_text(json.dumps([{'id':'s1','t':'你好','duration':2},
          {'id':'s2','t':'你好','duration':2}],ensure_ascii=False),encoding='utf-8')
        result=call('python3',SCRIPTS/'build_tasks.py','script.json','tasks.json','--persona','persona.json',cwd=self.p)
        self.assertEqual(result.returncode,0,result.stderr)
        (self.p/'results.json').write_text(json.dumps({'s1':{'src':'a.mp4'},'s2':{'src':'a.mp4'}}),encoding='utf-8')
        result=call('python3',SCRIPTS/'import_muse.py','tasks.json','results.json','clips.json',cwd=self.p)
        self.assertEqual(result.returncode,0,result.stderr)
        clips=json.loads((self.p/'clips.json').read_text())
        for item in clips.values(): item['review_status']='approved'
        (self.p/'clips.json').write_text(json.dumps(clips),encoding='utf-8')
        (self.p/'model.bin').write_bytes(b'test')
        whisper=self.p/'fake-whisper'
        whisper.write_text("#!/usr/bin/env python3\nimport json,sys\nfrom pathlib import Path\np=Path(sys.argv[sys.argv.index('-of')+1]+'.json')\np.write_text(json.dumps({'transcription':[{'text':'你好','offsets':{'from':0,'to':500}}]},ensure_ascii=False))\n",encoding='utf-8')
        whisper.chmod(0o755)
        self.whisper=whisper

    def tearDown(self): self.temp.cleanup()

    def test_assemble_and_align_are_non_destructive(self):
        cmd=['python3',SCRIPTS/'assemble.py','script.json','clips.json','--out','out.mp4',
             '--model','model.bin','--whisper-cli',self.whisper,'--keep-frames','s1=30']
        result=call(*cmd,cwd=self.p)
        self.assertEqual(result.returncode,0,result.stderr)
        qa=json.loads((self.p/'cut/qa.json').read_text())
        self.assertEqual(qa[0]['explicit_keep_frames'],30)
        self.assertAlmostEqual(qa[0]['keep'],1.0)
        self.assertFalse(qa[0]['lip_sync_verified'])
        out=self.p/'out.mp4'; before=out.read_bytes()
        again=call(*cmd,cwd=self.p)
        self.assertNotEqual(again.returncode,0)
        self.assertEqual(before,out.read_bytes())
        align=call('python3',SCRIPTS/'align.py','script.json','--cut-dir','cut','--out','tl.json',cwd=self.p)
        self.assertEqual(align.returncode,0,align.stderr)
        t=json.loads((self.p/'tl.json').read_text())
        self.assertEqual(len(t['segs']),2)
        self.assertGreater(t['total'],1)
        before=(self.p/'tl.json').read_bytes()
        self.assertNotEqual(call('python3',SCRIPTS/'align.py','script.json','--cut-dir','cut','--out','tl.json',cwd=self.p).returncode,0)
        self.assertEqual(before,(self.p/'tl.json').read_bytes())

    def test_review_gate_requires_approval(self):
        clips=json.loads((self.p/'clips.json').read_text());clips['s2']['review_status']='pending'
        (self.p/'clips.json').write_text(json.dumps(clips),encoding='utf-8')
        result=call('python3',SCRIPTS/'assemble.py','script.json','clips.json','--out','new.mp4',
                    '--model','model.bin','--whisper-cli',self.whisper,cwd=self.p)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('尚未人工审核通过',result.stderr)
        self.assertFalse((self.p/'new.mp4').exists())

if __name__ == '__main__': unittest.main()
