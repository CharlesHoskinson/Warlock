#!/usr/bin/env python3
"""Execute the candidate Bash core against a fake compositor, never a desktop."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
HELPERS=Path(os.getenv('MOTION_HELPER_DIR',str(HERE)))
HYPRCTL=r'''#!/usr/bin/env python3
import json,os,re,sys
from pathlib import Path
root=Path(os.environ['MOTION_CORE_FAKE'])
w=json.loads((root/'window.json').read_text())
cmd=sys.argv[1]
if cmd=='clients':print(json.dumps([w]))
elif cmd=='activewindow':print(json.dumps({'address':os.getenv('MOTION_CORE_ACTIVE',w['address'])}))
elif cmd=='monitors':print(json.dumps([{'id':0,'name':'DP-1','focused':True,'activeWorkspace':{'name':'2'}}]))
elif cmd=='workspaces':print(json.dumps([{'name':'2'}]))
elif cmd=='dispatch':
 expression=sys.argv[2]
 with (root/'dispatch.jsonl').open('a') as stream:stream.write(json.dumps(expression)+'\n')
 if '.window.move(' in expression:
  match=re.search(r'workspace = "([^"]+)"',expression);w['workspace']['name']=match.group(1)
 elif '.window.pin(' in expression:w['pinned']=not w['pinned']
 (root/'window.json').write_text(json.dumps(w))
 print('ok')
else:sys.exit(1)
'''

class CoreTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  bin=self.root/'bin';bin.mkdir();exe=bin/'hyprctl';exe.write_text(HYPRCTL);exe.chmod(0o755)
  self.initial={'address':'0x10','stableId':'stable10','pid':100,'mapped':True,'monitor':0,'workspace':{'name':'2'},'pinned':True,'at':[79,88],'size':[641,377],'floating':True,'fullscreen':0}
  (self.root/'window.json').write_text(json.dumps(self.initial))
  self.env=dict(os.environ,PATH=str(bin)+':'+os.environ['PATH'],XDG_RUNTIME_DIR=str(self.root),MOTION_CORE_FAKE=str(self.root),HYPR_WINDOWCTL_FAMILY_SINGLE='1',HYPR_WINDOWCTL_PREVIEW_READY='1')
 def tearDown(self):self.temp.cleanup()
 def run_core(self,op,identity='stable10',pid='100'):
  return subprocess.run([str(HELPERS/'hypr-windowctl-core'),op,'0x10',identity,pid],env=self.env,capture_output=True,text=True)
 def window(self):return json.loads((self.root/'window.json').read_text())
 def activate(self,identity='stable10',pid='100',active='0x10'):
  env=dict(self.env,HYPR_WINDOWCTL_MOTION='0',MOTION_CORE_ACTIVE=active)
  return subprocess.run([str(HELPERS/'hypr-windowctl'),'activate','0x10',identity,pid],env=env,capture_output=True,text=True)
 def test_opt_out_activate_active_visible_minimizes(self):
  result=self.activate();self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(self.window()['workspace']['name'],'special:win-minimized')
 def test_opt_out_activate_inactive_visible_restores_and_preserves_geometry(self):
  result=self.activate(active='0xother');self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(self.window(),self.initial)
  commands=(self.root/'dispatch.jsonl').read_text();self.assertIn('focus',commands);self.assertNotIn('special:win-minimized',commands)
 def test_opt_out_activate_minimized_restores(self):
  self.assertEqual(self.run_core('minimize').returncode,0)
  result=self.activate(active='0xother');self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(self.window(),self.initial)
 def test_opt_out_activate_stale_identity_cannot_dispatch(self):
  for identity,pid in [('stale','100'),('stable10','101')]:
   result=self.activate(identity,pid);self.assertEqual(result.returncode,3,result.stderr)
   self.assertFalse((self.root/'dispatch.jsonl').exists())
  self.assertEqual(self.window(),self.initial)
 def test_min_restore_preserve_exact_geometry_and_pin(self):
  result=self.run_core('minimize');self.assertEqual(result.returncode,0,result.stderr)
  minimized=self.window();self.assertEqual(minimized['workspace']['name'],'special:win-minimized');self.assertFalse(minimized['pinned'])
  self.assertEqual(minimized['at'],self.initial['at']);self.assertEqual(minimized['size'],self.initial['size'])
  result=self.run_core('restore');self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(self.window(),self.initial)
  commands=(self.root/'dispatch.jsonl').read_text()
  self.assertNotIn('resize',commands);self.assertNotIn('opacity',commands);self.assertNotIn('scratchpad',commands)
 def test_reused_identity_no_dispatch(self):
  result=self.run_core('minimize','stale','100');self.assertEqual(result.returncode,3)
  self.assertFalse((self.root/'dispatch.jsonl').exists());self.assertEqual(self.window(),self.initial)
 def test_reused_pid_no_dispatch(self):
  result=self.run_core('restore','stable10','101');self.assertEqual(result.returncode,3)
  self.assertFalse((self.root/'dispatch.jsonl').exists())
 def test_invalid_pid_no_dispatch(self):
  result=self.run_core('restore','stable10','not-a-number');self.assertEqual(result.returncode,2)
  self.assertFalse((self.root/'dispatch.jsonl').exists())
 def test_old_minimized_record_cannot_restore_stale_pin_or_desktop(self):
  self.assertEqual(self.run_core('minimize').returncode,0)
  state=self.window();state['stableId']='new10';state['pid']=200
  (self.root/'window.json').write_text(json.dumps(state))
  result=self.run_core('restore','new10','200');self.assertEqual(result.returncode,0,result.stderr)
  self.assertFalse(self.window()['pinned']);self.assertEqual(self.window()['workspace']['name'],'2')

if __name__=='__main__':unittest.main()
