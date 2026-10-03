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

class QSReplay(unittest.TestCase):
 def terminal(self,stage):
  import hashlib
  identity=dict(pid=99999991,start='1',pgid=99999991);row=dict(id='owned',pid=identity['pid'],shell_id=hashlib.md5(str(stage/'payload/omarchy/shell/shell.qml').encode()).hexdigest(),config_path=str(stage/'payload/omarchy/shell/shell.qml'),launch_time='2026-10-01T17:31:45');records=[]
  for n,(role,command,stdout) in enumerate([('startup-ping',[str(stage/'payload/omarchy/bin/omarchy-shell'),'shell','ping'],'ok\n'),('instance-selection',['/usr/bin/qs','--no-color','list','-a','-j'],json.dumps([row])),('normal-kill',['/usr/bin/qs','--no-color','kill','--pid',str(identity['pid'])],'Killed owned\n')]):records.append(dict(role=role,command=command,qsIdentity=identity,processIdentity=dict(pid=99999992+n,start='1'),startedNs=n*2+1,completedNs=n*2+2,returncode=0,stdout=stdout,stderr='',originalProbeGone=True))
  cleanup=dict(normalQuit=True,exitCode=0,exactOriginalGone=True,selectedInstance=row,records=records);v=dict(processes=[dict(role='taskbar-shell',identity=identity)],cleanup=dict(shell=cleanup),exactQSReadiness=dict(exactReady=True,identity=identity,records=records));j=dict(identity=identity,ready=True,killSent=True,records=records);return v,j
 def test_exact_probe_replay_and_no_natural_exit_promotion(self):
  stage=Path('/owned');v,j=self.terminal(stage);self.assertTrue(audit.qs_replay(v,stage,j));v['cleanup']['shell']['normalQuit']=False;self.assertFalse(audit.qs_replay(v,stage,j))
 def test_unknown_reply_wrong_pid_and_second_kill_refused(self):
  import copy
  for change in (lambda v,j:j['records'][0].update(stderr='unknown'),lambda v,j:j['records'][-1].update(command=['/usr/bin/qs','--no-color','kill','--pid','1']),lambda v,j:j['records'].append(copy.deepcopy(j['records'][-1]))):
   v,j=self.terminal(Path('/owned'));change(v,j);self.assertFalse(audit.qs_replay(v,Path('/owned'),j))
