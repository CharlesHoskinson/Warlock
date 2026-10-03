"""Actual fresh controller persistence and owned normal-process CPU tests.

Synthetic session data supplies no GUI/native acceptance authority.
"""
from pathlib import Path
import json,os,subprocess,sys,tempfile,time,unittest
from native_cases import NativeCases
class Inert:
 def __init__(self):self.fail=False
 def guard(self):
  if self.fail:raise RuntimeError('Actual injected pre-observation ownership refusal')
 def data(self,name):
  if name!='clients':raise RuntimeError('Unexpected synthetic query')
  return []
class Proof(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.s=Inert();self.c=NativeCases(self.s,Path(self.temp.name)/'case')
 def tearDown(self):self.temp.cleanup()
 def record(self):return json.loads((self.c.output/'cases.json').read_text())
 def test_error_retained_before_outcome(self):
  with self.assertRaises(ValueError):self.c.observe('actual failure',lambda:json.loads('{'))
  row=self.record()['observations'][0];self.assertEqual(row['label'],'actual failure');self.assertIn('error',row);self.assertNotIn('value',row);self.assertFalse(self.record()['nativeFeatureAccepted'])
 def test_guard_refusal_does_not_execute_reader(self):
  self.s.fail=True;called=[]
  with self.assertRaises(RuntimeError):self.c.observe('guard refusal',lambda:called.append(1))
  self.assertEqual(called,[]);self.assertIn('ownership refusal',self.record()['observations'][0]['error'])
 def test_bounded_failed_wait_retains_every_actual_poll(self):
  with self.assertRaises(RuntimeError):self.c.wait('no readiness',lambda:False,.08)
  rows=self.record()['observations'];self.assertGreaterEqual(len(rows),2);self.assertTrue(all(r['value'] is False for r in rows));self.assertFalse(self.record()['nativeFeatureAccepted'])
 def test_missing_receipt_tokens_refuse(self):
  self.s.ctl=lambda *args:'null';self.c.query=lambda name:[]
  self.c.own=lambda name:dict(address='0xabc',stableId='18000000',pid=os.getpid())
  with self.assertRaises(ValueError):self.c.capture('owner')
 def test_actual_owned_normal_quit_and_ack(self):
  source='''import json,sys,time\nfrom pathlib import Path\np=Path(sys.argv[1])\nwhile True:\n try:r=json.loads((p/'command.json').read_text())\n except FileNotFoundError:time.sleep(.01);continue\n if r['command']=='quit':\n  (p/'events.jsonl').write_text(json.dumps(dict(event='commandHandled',command='quit',epoch=r['epoch']))+'\\n');break\n time.sleep(.01)\n'''
  child=subprocess.Popen(['/usr/bin/python3','-I','-S','-c',source,str(self.c.output)],start_new_session=True)
  try:
   self.c.fixture=child;self.c.close();row=self.record()['cleanup']['fixture'];self.assertEqual(row['exitCode'],0);self.assertTrue(row['gone']);self.assertFalse(row['forced']);self.assertTrue(self.record()['normalCleanup']);self.assertFalse(self.record()['nativeFeatureAccepted'])
  finally:
   if child.poll()is None:child.terminate();child.wait(timeout=3)
 def test_cleanup_error_never_accepts(self):
  class Dead:
   pid=99999999
   def poll(self):return 7
  self.c.fixture=Dead()
  with self.assertRaises(RuntimeError):self.c.close()
  self.assertEqual(self.record()['result'],'fail');self.assertFalse(self.record()['normalCleanup']);self.assertIn('error',self.record()['cleanup']['fixture'])
if __name__=='__main__':unittest.main()
