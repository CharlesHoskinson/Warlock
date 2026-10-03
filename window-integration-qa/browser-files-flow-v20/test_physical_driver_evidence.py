"""Actual unprojected B20 owner collector CPU/kernel and exact source comparisons."""
import ast,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from physical_driver_evidence import PhysicalDriverEvidence,matched_owner
from physical_preservation_projection import project
B=Path(__file__).resolve().parent
EXPECTED={'address':'0x123','stableId':31,'pid':os.getpid()}
def start(pid):return Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19]
class Obs:
 def __init__(self):self.environment={'XDG_RUNTIME_DIR':'/private','WAYLAND_DISPLAY':'wayland-1','HYPRLAND_INSTANCE_SIGNATURE':'private'};self.state={'keyboardSurfacePresent':True,'keyboardResourcePresent':True,'keyboardOwner':dict(EXPECTED),'coreNativeFocus':dict(EXPECTED)};self.clients=[dict(EXPECTED)];self.starts=start(os.getpid());self.raw=None
 def start(self,pid):return self.starts
 def data(self,name):assert name=='clients';return self.clients
 def run(self,*args):return self.raw if self.raw is not None else json.dumps(self.state)
class Evidence(unittest.TestCase):
 def collector(self,d,obs):return PhysicalDriverEvidence(Path(d)/'proof.json',obs,lambda:{'nativeFocus':dict(EXPECTED)},os.getpid(),start(os.getpid()),EXPECTED,lambda:None)
 def test_actual_unprojected_driver_substitution_exact_source_inverse(self):
  current=(B/'private_session.py').read_text();self.assertEqual(project(B/'private_session.py',current),(B.parent/'browser-files-flow-v19/private_session.py').read_text());self.assertNotIn('/usr/bin/wtype',current);self.assertEqual(current.count("str(B/'physical-keyboard')"),3);self.assertIn('continuation_trace.run_wtype',current)
 def test_original15_check_asts_and_continuation_equality_unchanged(self):
  def checks(p):return[ast.dump(n,include_attributes=False)for n in ast.walk(ast.parse(p.read_text()))if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='check']
  self.assertEqual(checks(B/'private_session.py'),checks(B.parent/'browser-files-flow-v19/private_session.py'))
  old=(B.parent/'browser-files-flow-v19/private_session.py').read_text();new=(B/'private_session.py').read_text()
  for line in old.splitlines():
   if 'expected='in line or 'actual continuation at retained caret'in line or 'old_inputs='in line:self.assertIn(line,new)
 def test_actual_owned_cpu_child_argv_exe_exit_evidence(self):
  with tempfile.TemporaryDirectory()as d:
   obs=Obs();e=self.collector(d,obs);r=e.run([str(B/'physical-keyboard'),'--plan','-d','20','--','-continued0'],{},12);self.assertEqual(r.returncode,0);p=json.loads((Path(d)/'proof.json').read_text());row=p['commands'][0];self.assertTrue(row['before']['accepted']);self.assertTrue(row['after']['accepted']);self.assertTrue(row['normalExit']);self.assertTrue(row['pidPathAbsentAfterWait']);self.assertEqual(row['actualOwnedProcess']['identity']['pid'],row['pid']);self.assertFalse(p['originalFeatureAcceptance'])
 def test_boolean_zeros_no_owner_authority(self):
  for k in ('keyboardSurfacePresent','keyboardResourcePresent'):
   o=Obs();o.state[k]=1;self.assertFalse(matched_owner(o.state,EXPECTED))
 def test_numeric_identity_bools_refused(self):
  o=Obs();o.state['keyboardOwner']['stableId']=True;self.assertFalse(matched_owner(o.state,EXPECTED))
 def test_wrong_seat_refuses_before_spawn(self):
  with tempfile.TemporaryDirectory()as d:
   o=Obs();o.state['keyboardOwner']['pid']=123;e=self.collector(d,o)
   with patch('physical_driver_evidence.subprocess.Popen')as spawn:
    with self.assertRaises(AssertionError):e.run(['unreachable'],{},12)
    spawn.assert_not_called()
   row=json.loads((Path(d)/'proof.json').read_text())['commands'][0];self.assertIn('seatKeyboardRaw',row['before']);self.assertFalse(row['before']['accepted'])
 def test_wrong_core_refuses_before_spawn(self):
  with tempfile.TemporaryDirectory()as d:
   o=Obs();o.state['coreNativeFocus']['address']='0x456';e=self.collector(d,o)
   with patch('physical_driver_evidence.subprocess.Popen')as spawn:
    with self.assertRaises(AssertionError):e.run(['unreachable'],{},12)
    spawn.assert_not_called()
 def test_malformed_raw_retained_before_parse_failure(self):
  with tempfile.TemporaryDirectory()as d:
   o=Obs();o.raw='not json';e=self.collector(d,o)
   with self.assertRaises(ValueError):e.run(['unreachable'],{},12)
   self.assertEqual(json.loads((Path(d)/'proof.json').read_text())['commands'][0]['before']['seatKeyboardRaw'],'not json')
 def test_lifetime_change_before_no_spawn(self):
  with tempfile.TemporaryDirectory()as d:
   o=Obs();e=self.collector(d,o);o.starts='1'
   with patch('physical_driver_evidence.subprocess.Popen')as spawn:
    with self.assertRaises(AssertionError):e.run(['unreachable'],{},12)
    spawn.assert_not_called()
 def test_actual_late_owner_change_refuses_after_delegate_no_retry(self):
  with tempfile.TemporaryDirectory()as d:
   o=Obs();e=self.collector(d,o);calls=[]
   def delegate(cmd,env):calls.append(cmd);o.state['keyboardOwner']['pid']=123;return subprocess.CompletedProcess(cmd,0,'','')
   with self.assertRaises(AssertionError):e.run(['delegate'],{},12,delegate)
   self.assertEqual(len(calls),1);self.assertFalse(e.proof['commands'][0]['after']['accepted'])
 def test_actual_bad_exit_no_retry(self):
  with tempfile.TemporaryDirectory()as d:
   o=Obs();e=self.collector(d,o)
   with self.assertRaises(AssertionError):e.run(['/usr/bin/python3','-c','raise SystemExit(7)'],{},8)
   self.assertEqual(e.proof['commands'][0]['returncode'],7);self.assertEqual(len(e.proof['commands']),1)
 def test_setup_selectors_change_terminal(self):
  with tempfile.TemporaryDirectory()as d:
   o=Obs();e=self.collector(d,o);o.environment['WAYLAND_DISPLAY']='foreign'
   with self.assertRaises(AssertionError):e.run(['unreachable'],{},12)
 def test_formal_before_wrapper_and_real_driver(self):
  r=json.loads((B/'physical-owner-formal-before-wrapper.json').read_text());self.assertEqual(r['result'],'pass');self.assertTrue(r['wrapperAbsent']);self.assertTrue(r['privateSessionExactB19']);self.assertFalse(r['nativeExecuted'])
if __name__=='__main__':unittest.main()
