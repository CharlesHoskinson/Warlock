import io,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from main_observer import MainObserver
import producer_control as c
class ProducerTests(unittest.TestCase):
 def test_real_non_input_sync_only_handshake(self):
  script="import sys\nfor line in sys.stdin:\n if line!='sync\\n':sys.exit(91)\n print('ready',flush=True)\n"
  p=subprocess.Popen(['/usr/bin/python3','-c',script],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   report={};row=c.ready(p,report);self.assertTrue(row['pass_']);self.assertFalse(row['inputSent']);self.assertEqual(row['response'],'ready')
  finally:p.communicate(timeout=3)
  self.assertEqual(p.returncode,0)
 def test_actual_native_guards_refuse_main_before_connection_with_exit_diagnostic(self):
  for name in ('native-input','native-pointer'):
   binary=Path(__file__).parent/'native-fixture'/name
   env={**os.environ,'XDG_RUNTIME_DIR':'/run/user/'+str(os.getuid()),'WAYLAND_DISPLAY':'wayland-0','HYPR_A11Y_BRIDGE_PRIVATE':'1'}
   p=subprocess.Popen(['/usr/bin/prlimit','--core=1:1','--',str(binary)],env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
   report={}
   with self.assertRaisesRegex(RuntimeError,'producer startup failed'):c.ready(p,report)
   self.assertEqual(report['producerReadiness'][0]['exitCode'],20);self.assertIn('main and legacy tmp forbidden',report['producerReadiness'][0]['stderrTail'])
   for pipe in (p.stdin,p.stdout,p.stderr):pipe.close()
 def test_invalid_reply_is_refused_before_any_input(self):
  p=subprocess.Popen(['/usr/bin/python3','-c',"import sys;sys.stdin.readline();print('almost-ready',flush=True)"],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  report={}
  with self.assertRaisesRegex(RuntimeError,'producer startup failed'):c.ready(p,report)
  self.assertFalse(report['producerReadiness'][0]['pass_']);self.assertFalse(report['producerReadiness'][0]['inputSent'])
  for pipe in (p.stdin,p.stdout,p.stderr):pipe.close()
 def test_focus_identity_preserved_across_title_only_change(self):
  before={key:None for key in ('clients','focus','cursor','outputs','a11y','reader','files','plugins','keyboards','catalogs','clipboard','configErrors')}
  before.update(clients=[],reader='false',files={'visible':True},focus={'address':'0x1','stableId':'s1','pid':2,'title':'before'})
  after={**before,'focus':{**before['focus'],'title':'after'}}
  self.assertTrue(MainObserver.compare(before,after)['focus']);self.assertNotEqual(before['focus'],after['focus'])
  for key,value in [('address','0x2'),('stableId','s2'),('pid',3)]:
   after['focus']={**before['focus'],key:value};self.assertFalse(MainObserver.compare(before,after)['focus'],key)
if __name__=='__main__':unittest.main()
