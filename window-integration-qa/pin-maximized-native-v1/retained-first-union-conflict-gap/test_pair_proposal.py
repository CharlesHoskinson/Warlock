"""CPU source conservation and actual kernel process binding faults; no desktop."""
import ast,hashlib,importlib.util,json,os,subprocess,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
B=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pair_binding',B/'proposed/pair_binding.py');binding=importlib.util.module_from_spec(spec);spec.loader.exec_module(binding)
def method(path,cls,name):
 tree=ast.parse(path.read_text());c=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name==cls)
 n=next(n for n in c.body if isinstance(n,ast.FunctionDef)and n.name==name)
 return ast.dump(n,include_attributes=False)
class PairProposal(unittest.TestCase):
 def test_original14_source_and_observer_exact(self):
  row=json.loads((B/'a3-component.json').read_text())
  for source,metadata in row['sources'].items():
   src=Path(source);saved=B/'retained-a3'/src.relative_to(Path('/home/hoskinson/window-integration-qa/pin-native-qa-v3'))
   self.assertTrue(src.is_file(),source);self.assertTrue(saved.is_file(),str(saved))
   self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),metadata['sha256'])
   self.assertEqual(src.stat().st_mode&0o7777,metadata['mode'])
   self.assertEqual(src.read_bytes(),saved.read_bytes())
 def test_entire_entry_only_core_selector(self):
  before=method(B/'inverses/original-host.py','PrivateHyprSession','__enter__')
  after=method(B/'proposed/candidate_host.py','PrivateHyprSession','__enter__')
  text=(B/'proposed/candidate_host.py').read_text().replace("[str(CORE),'--config',str(config)]","['/usr/bin/Hyprland','--config',str(config)]")
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)/'source.py';p.write_text(text)
   self.assertEqual(before,method(p,'PrivateHyprSession','__enter__'))
 def test_wait_socket_only_registered_core_selector(self):
  text=(B/'proposed/candidate_host.py').read_text().replace("row.get('command',[None])[0]==str(CORE)","row.get('command',[None])[0]=='/usr/bin/Hyprland'")
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)/'source.py';p.write_text(text)
   self.assertEqual(method(B/'inverses/bootstrap-host.py','ReviewedWestonHost','wait_socket'),method(p,'ReviewedWestonHost','wait_socket'))
 def test_launch_exact_guard_and_aq_original_parent(self):
  text=(B/'proposed/candidate_host.py').read_text().replace('verify_inputs(); verify_pair()','verify_inputs()').replace('str(command[0])!=str(CORE)',"str(command[0])!='/usr/bin/Hyprland'").replace('return original.PrivateWestonHost.launch(self,name,command,selected)','return super().launch(name,command,selected)')
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)/'source.py';p.write_text(text)
   self.assertEqual(method(B/'inverses/bootstrap-host.py','ReviewedWestonHost','launch'),method(p,'ReviewedWestonHost','launch'))
 def test_output_budget_and_shutdown_unchanged(self):
  a=(B/'proposed/private_output_host.py').read_text().replace("QA=Path('/home/hoskinson/window-integration-qa')","QA=Path(__file__).resolve().parent.parent")
  self.assertEqual(a,(B/'retained-a3/private_output_host.py').read_text())
 def test_proposal_not_usable(self):
  with self.assertRaises(FileNotFoundError):binding.read_pair(B/'PAIR_READY.json')
 def test_incomplete_and_bool_build_are_refused(self):
  with tempfile.TemporaryDirectory()as tmp:
   p=Path(tmp)/'pair.json'
   for row in [{},{'buildComplete':1,'sourceProposalOnly':False},{'buildComplete':True,'sourceProposalOnly':True}]:
    p.write_text(json.dumps(row))
    with self.assertRaises(RuntimeError):binding.read_pair(p)
 def test_actual_kernel_process_record_and_wrong_exe_refused(self):
  child=subprocess.Popen(['/usr/bin/cat'],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL)
  try:
   deadline=time.monotonic()+2
   while True:
    snap=binding.process_snapshot(child.pid)
    if snap['exe']=='/usr/bin/cat':break
    if time.monotonic()>=deadline:raise AssertionError('fixture exec deadline')
   session=SimpleNamespace(evidence=dict(compositorPID=child.pid,compositorStart=snap['start'],compositorPGID=snap['pgid'],compositorConfig='/tmp/never-native-config'))
   row=dict(inputs={str(binding.CORE):'0'*64},coreELFBuildID='0'*40,sourceReadySHA256='0'*64)
   raw=binding.attest(session,row,'CPU-wrong-executable')
   self.assertFalse(raw['passed']);self.assertEqual(raw['before']['exe'],'/usr/bin/cat');self.assertTrue(raw['rawMaps'])
   session.evidence['compositorStart']='0';self.assertFalse(binding.attest(session,row,'CPU-replaced-lifetime')['passed'])
  finally:
   child.stdin.close();child.wait(timeout=2)
 def test_typed_pid_refusal(self):
  for pid in [True,False,0,-1,1.0,'1']:
   with self.assertRaises(RuntimeError):binding.process_snapshot(pid)
class ClosureUnion(unittest.TestCase):
 def module(self):
  spec=importlib.util.spec_from_file_location('closure_union',B/'proposed/closure_union.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 def test_nested_manifest_and_declared_modes(self):
  m=self.module()
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);(root/'ancestor').mkdir();p=root/'ancestor/frozen-inputs.json';p.write_text('nested manifest');p.chmod(0o600)
   own=root/'frozen-inputs.json';own.write_text('own excluded');own.chmod(0o600)
   row=dict(inputs={str(p):m.digest(p)},inputModes={str(p):0o600},symlinks={})
   result=m.union(root,[row]);self.assertIn(str(p),result['inputs']);self.assertNotIn(str(own),result['inputs']);self.assertEqual(result['inputModes'][str(p)],0o600)
   p.chmod(0o644)
   with self.assertRaises(RuntimeError):m.union(root,[row])
 def test_changed_ancestral_bytes_refused(self):
  m=self.module()
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);p=root/'failure.json';p.write_text('retained failure');p.chmod(0o600)
   row=dict(inputs={str(p):m.digest(p)},inputModes={str(p):0o600},symlinks={})
   p.write_text('replaced')
   with self.assertRaises(RuntimeError):m.union(root,[row])
 def test_intentional_byte_link_alias_exact(self):
  m=self.module()
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);p=root/'target';p.write_text('target bytes');p.chmod(0o600);alias=root/'alias';alias.symlink_to('target')
   row=dict(inputs={str(alias):m.digest(alias)},inputModes={str(alias):0o600},symlinks={str(alias):'target'})
   result=m.union(root,[row]);self.assertEqual(result['inputs'][str(alias)],m.digest(p));self.assertEqual(result['symlinks'][str(alias)],'target')
if __name__=='__main__':unittest.main(verbosity=2)
