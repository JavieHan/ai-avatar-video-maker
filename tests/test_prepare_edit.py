"""Local, synthetic-media checks for the community Remotion project preparer."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'skills/digital-human-koubo-muse/scripts/prepare_edit.py'

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'ffmpeg/ffprobe required')
class PrepareEditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='koubo-prepare-test-')
        self.base=Path(self.temp.name)
        self.video=self.base/'video.mp4'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=320x512:r=24:d=1',
                        '-f','lavfi','-i','sine=frequency=440:duration=1', '-c:v','libx264',
                        '-pix_fmt','yuv420p','-c:a','aac','-shortest',str(self.video)],check=True)
        self.timeline=self.base/'tl.json'
        self.timeline.write_text(json.dumps({'total':1,'segs':[{'id':'s1','start':0,'end':1,
                                 'text':'测试字幕','chars':{'0':0}}]},ensure_ascii=False),encoding='utf-8')
    def tearDown(self): self.temp.cleanup()
    def run_prepare(self,*args):
        return subprocess.run([sys.executable,str(SCRIPT),'--video',str(self.video),'--timeline',str(self.timeline),
                               '--output',str(self.base/'edit'),*args],capture_output=True,text=True)
    def test_blank_user_project_preserves_frame_and_original_audio(self):
        result=self.run_prepare()
        self.assertEqual(result.returncode,0,result.stderr)
        edit=json.loads((self.base/'edit/src/edit.json').read_text())
        self.assertEqual((edit['width'],edit['height']),(320,512))
        self.assertEqual(edit['video'],'main.mp4')
        self.assertIsNone(edit['voice'])
        self.assertIsNone(edit['music'])
        self.assertEqual(edit['stickers'],[])
        self.assertEqual((self.base/'edit/public/main.mp4').read_bytes(),self.video.read_bytes())
        self.assertEqual(json.loads((self.base/'edit/src/tl.json').read_text())['segs'][0]['text'],'测试字幕')
    def test_existing_output_is_never_overwritten(self):
        target=self.base/'edit';target.mkdir();marker=target/'keep.txt';marker.write_text('original')
        result=self.run_prepare()
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(marker.read_text(),'original')
        self.assertIn('不覆盖',result.stderr)
    def test_replacement_voice_is_explicit_and_user_stickers_are_optional(self):
        voice=self.base/'voice.wav'
        subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','sine=frequency=660:duration=1',str(voice)],check=True)
        stickers=self.base/'stickers.json'
        stickers.write_text(json.dumps([{'start':0.1,'end':0.9,'title':'测试','tags':['画面']}],ensure_ascii=False))
        result=self.run_prepare('--voice',str(voice),'--stickers',str(stickers))
        self.assertEqual(result.returncode,0,result.stderr)
        edit=json.loads((self.base/'edit/src/edit.json').read_text())
        self.assertEqual(edit['voice'],'voice.wav')
        self.assertEqual(edit['stickers'][0]['title'],'测试')
        self.assertEqual((self.base/'edit/public/voice.wav').read_bytes(),voice.read_bytes())
        self.assertIn('不驱动口型',result.stdout)
    def test_render_script_refuses_existing_output(self):
        output=self.base/'existing.mp4'
        output.write_bytes(b'untouched')
        render=ROOT/'skills/digital-human-koubo-muse/templates/huazi-916/scripts/render.sh'
        result=subprocess.run(['bash',str(render),str(output)],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(output.read_bytes(),b'untouched')
        self.assertIn('不覆盖',result.stderr)
    def test_rejects_out_of_range_caption(self):
        self.timeline.write_text(json.dumps({'total':9,'segs':[{'start':0,'end':9,'text':'测试'}]}))
        result=self.run_prepare()
        self.assertNotEqual(result.returncode,0)
        self.assertFalse((self.base/'edit').exists())

if __name__=='__main__': unittest.main()
