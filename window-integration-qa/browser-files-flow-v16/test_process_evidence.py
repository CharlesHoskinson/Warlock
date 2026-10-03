import base64,unittest,tempfile
from pathlib import Path
from process_evidence import classify,renderer,BINARY,snapshot
class ProcessEvidence(unittest.TestCase):
 def rec(self,raw=None):
  return {'identity':{'pid':123,'start':'77'},'rawCmdlineBase64':base64.b64encode(raw or (BINARY.encode()+b'\0--type=renderer\0')).decode(),'status':'Uid: 1000 1000 1000 1000\nSeccomp: 2\nNoNewPrivs: 1\n','statusFields':{'Uid':'1000 1000 1000 1000','Seccomp':'2','NoNewPrivs':'1'},'netNamespace':'net:[2]','userNamespace':'user:[3]','lifetimeBefore':True,'lifetimeAfter':True,'errors':{},'exitedDuringObservation':False,'nulSplit':[]}
 def test_exact_vector(self):self.assertEqual(classify(BINARY.encode()+b'\0--type=renderer\0')['role'],'renderer')
 def test_flattened_title(self):self.assertEqual(classify(BINARY.encode()+b' --type=renderer --lang=en-US\0')['role'],'renderer')
 def test_padded_title(self):self.assertEqual(classify(BINARY.encode()+b' --type=renderer\0\0\0')['role'],'renderer')
 def test_value_not_role(self):self.assertIsNone(classify(BINARY.encode()+b' --foo= --type=renderer\0')['role'])
 def test_wrong_executable(self):self.assertIsNone(classify(b'/other/brave --type=renderer\0')['role'])
 def test_conflicting_roles(self):self.assertIsNone(classify(BINARY.encode()+b'\0--type=renderer\0--type=utility\0')['role'])
 def test_duplicate_role(self):self.assertIsNone(classify(BINARY.encode()+b' --type=renderer --type=renderer\0')['role'])
 def test_missing_terminator(self):self.assertIsNone(classify(BINARY.encode()+b' --type=renderer')['role'])
 def test_ambiguous_title(self):self.assertIsNone(classify(BINARY.encode()+b' --type=renderer --foo="two words"\0')['role'])
 def test_disabled_sandbox(self):
  with self.assertRaises(RuntimeError):classify(BINARY.encode()+b' --type=renderer --no-sandbox\0')
 def test_real_sandbox_fields(self):self.assertEqual(renderer(self.rec(),1000,'net:[1]')['seccomp'],'2')
 def test_unreadable_live_refused(self):
  r=self.rec();del r['netNamespace']
  with self.assertRaises(RuntimeError):renderer(r,1000,'net:[1]')
 def test_uid_refused(self):
  r=self.rec();r['statusFields']['Uid']='1000 0 1000 1000'
  with self.assertRaises(RuntimeError):renderer(r,1000,'net:[1]')
 def test_host_network_refused(self):
  with self.assertRaises(RuntimeError):renderer(self.rec(),1000,'net:[2]')
 def test_seccomp_refused(self):
  r=self.rec();r['statusFields']['Seccomp']='0'
  with self.assertRaises(RuntimeError):renderer(r,1000,'net:[1]')
 def test_no_new_privileges_refused(self):
  r=self.rec();r['statusFields']['NoNewPrivs']='0'
  with self.assertRaises(RuntimeError):renderer(r,1000,'net:[1]')
 def test_exited_record_retained_not_renderer(self):
  r=self.rec();r['exitedDuringObservation']=True;self.assertIsNone(renderer(r,1000,'net:[1]'))
 def test_snapshot_retains_unreadable_and_raw_bytes(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);p=root/'123';p.mkdir();(p/'cmdline').write_bytes(BINARY.encode()+b' --type=renderer\0');(p/'status').write_text('Uid: 1000 1000 1000 1000\n');(p/'stat').write_text('fixture stat')
   r=snapshot({'pid':123,'start':'77'},lambda identity:True,root)
   self.assertEqual(base64.b64decode(r['rawCmdlineBase64']),BINARY.encode()+b' --type=renderer\0');self.assertEqual(r['statusFields']['Uid'],'1000 1000 1000 1000');self.assertIn('exe',r['errors']);self.assertIn('netNamespace',r['errors'])
 def test_snapshot_captures_lifetime_race(self):
  answers=iter([True,False])
  with tempfile.TemporaryDirectory() as tmp:
   r=snapshot({'pid':123,'start':'77'},lambda identity:next(answers),Path(tmp));self.assertTrue(r['exitedDuringObservation']);self.assertTrue(r['errors'])
if __name__=='__main__':unittest.main(verbosity=2)
