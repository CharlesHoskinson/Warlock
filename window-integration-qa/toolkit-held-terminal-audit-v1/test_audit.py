import importlib.util,json,os,sys,tempfile,unittest
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));import audit
class Replay(unittest.TestCase):
 def test_descriptor_refuses_symlink_and_preserves_full_eof(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'p';p.write_bytes(b'exact\n');q=Path(folder)/'q';q.symlink_to(p)
   self.assertEqual(audit.read(p),b'exact\n')
   with self.assertRaises(OSError):audit.read(q)
 def test_exact_pidstart_not_pid_only(self):
  data=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split();row=dict(pid=os.getpid(),start=data[19],pgid=int(data[2]));self.assertFalse(audit.gone(row));self.assertTrue(audit.gone(dict(row,start='0')))
 def test_fake_releases_unknown_commands_and_unbalanced_transitions_refused(self):
  clean=dict(exitCode=0,normalEOF=True,knownDownTransitionsReleased=True,identity=dict(pid=99999999,start='1'),trace=[dict(pid=99999999,start='1',sentNs=1,command='button 272 1'),dict(pid=99999999,start='1',sentNs=2,command='button 272 0')])
  self.assertTrue(audit.input_replay(clean,'pointer'))
  clean['trace']=clean['trace'][:1];self.assertFalse(audit.input_replay(clean,'pointer'))
  clean['trace']=[dict(pid=99999999,start='1',sentNs=1,command='markReleased')];self.assertFalse(audit.input_replay(clean,'pointer'))
 def test_group_member_order_and_lifetimes_remain_distinct(self):
  a=dict(address='0xa',stableId='1',pid=123);b=dict(address='0xb',stableId='2',pid=123);g=dict(head=a,current=a,members=[a,b],locked=False,denied=False)
  self.assertNotEqual(audit.groups(dict(groups=[g])),audit.groups(dict(groups=[dict(g,members=[b,a])])))
  self.assertFalse(audit.eq(a,dict(a,stableId='3')))
 def test_native_bool_pid_and_nan_rectangle_refused(self):
  with self.assertRaises(ValueError):audit.identity(dict(address='0xa',stableId='1',pid=True))
  self.assertFalse(audit.inside([float('nan'),0],[0,0,10,10]))
if __name__=='__main__':unittest.main(verbosity=2)
