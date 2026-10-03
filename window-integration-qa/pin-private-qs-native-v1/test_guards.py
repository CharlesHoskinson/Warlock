"""Focused actual CPU publication and new-source guards; no Qt/GUI authority."""
from pathlib import Path
import ast,copy,json,os,stat,tempfile,unittest
from unittest.mock import patch
import io_guard as io
from selection import B,LIFE_SCHEDULE,CORE_SHA,PLUGIN_SHA,HELPER_SHA,PROVIDER,COMPOSITION
from run_native import gate_phase,native_class
from route_runtime import process_state,load_controller
from materialize import exact_exec
from root_functions import original_functions,SOURCE
def state(role='toggle'):
 r=dict(schema='qml-pin-process-lifecycle-v1',lease=1,fault=False,exitCode=0,nativeWrites=0,automaticRetries=0,stderr='',evidence={})
 for k in('started','exited','normalExit','stdoutEOF','stderrEOF','workerCreated','workerFinished','workerJoined','kernelGone','receiptVerified','normalLifecycle','historicalKernelProof','current','kernelBound','complete'):r[k]=True
 receipt=dict(result='captured'if role=='capture'else'complete',automaticRetries=0,nativeCompletionClaimed=role=='toggle')
 if role=='capture':receipt['nativeWrites']=0
 r['stdout']=json.dumps(receipt);return r
class Tests(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory(dir=B,prefix='cpu-');self.folder=Path(self.temp.name);self.folder.chmod(0o700)
 def tearDown(self):self.temp.cleanup()
 def test_exclusive_full_publication(self):
  p=self.folder/'receipt';raw=b'x'*8193;io.publish(p,raw);self.assertEqual(p.read_bytes(),raw);self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
  with self.assertRaises(FileExistsError):io.publish(p,b'overwrite')
  self.assertEqual(p.read_bytes(),raw)
 def test_actual_short_writes_advance(self):
  real=os.write
  with patch('io_guard.os.write',side_effect=lambda fd,raw:real(fd,raw[:7])):io.publish(self.folder/'short',b'0123456789'*19)
  self.assertEqual((self.folder/'short').read_bytes(),b'0123456789'*19)
 def test_zero_write_refuses(self):
  with patch('io_guard.os.write',return_value=0):
   with self.assertRaises(OSError):io.publish(self.folder/'zero',b'a')
 def test_symlink_parent_and_target_refuse(self):
  target=self.folder/'data';target.write_bytes(b'kept');link=self.folder/'link';link.symlink_to(target)
  with self.assertRaises(FileExistsError):io.publish(link,b'wrong')
  alias=self.folder/'alias';alias.symlink_to(self.folder,target_is_directory=True)
  with self.assertRaises(ValueError):io.publish(alias/'new',b'wrong')
  self.assertEqual(target.read_bytes(),b'kept')
 def test_directory_special_mode_refuses(self):
  self.folder.chmod(0o1700)
  with self.assertRaises(ValueError):io.directory(self.folder)
  self.folder.chmod(0o700)
 def test_duplicate_nonfinite_json_refuses(self):
  for raw in ('{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}'):
   with self.subTest(raw=raw),self.assertRaises(ValueError):io.strict(raw)
 def test_inventory_actual_mutation_refuses(self):
  p=self.folder/'source';p.write_bytes(b'one');p.chmod(0o600);r=dict(inputs={str(p):io.sha(p)},inputModes={str(p):0o600},symlinks={});io.verify(r);p.write_bytes(b'two')
  with self.assertRaises(ValueError):io.verify(r)
 def test_inventory_literal_link_mutation_refuses(self):
  p=self.folder/'one';p.write_bytes(b'a');other=self.folder/'two';other.write_bytes(b'a');link=self.folder/'link';link.symlink_to(p);r=dict(inputs={str(p):io.sha(p)},inputModes={str(p):stat.S_IMODE(p.stat().st_mode)},symlinks={str(link):str(p)});io.verify(r);link.unlink();link.symlink_to(other)
  with self.assertRaises(ValueError):io.verify(r)
 def test_no_native_grant(self):
  p=self.folder/'frozen';p.write_bytes(b'fixture')
  for g in ({},{'nativeAuthorized':1},{'nativeAuthorized':True,'manifestSHA256':'0'*64,'phase':'cold-baseline'}):
   with self.subTest(g=g),self.assertRaises(ValueError):gate_phase(g,'cold-baseline',p)
 def test_reliability_needs_all_five_actual_routes(self):
  p=self.folder/'frozen';p.write_bytes(b'fixture');proof=self.folder/'review';io.publish_json(proof,dict(accepted=True,selectedCoreSHA256=CORE_SHA,selectedPluginSHA256=PLUGIN_SHA,providerSHA256=io.sha(PROVIDER),ordinaryHelperSHA256=HELPER_SHA,sourceManifestSHA256=io.sha(p),requiredRoutes={'normalChanged':True}))
  g=dict(nativeAuthorized=True,manifestSHA256=io.sha(p),phase='reliability',requiredRoutesReview=str(proof),requiredRoutesReviewSHA256=io.sha(proof))
  with self.assertRaises(ValueError):gate_phase(g,'reliability',p)
 def test_positive_metadata_and_cancelled_denial(self):
  for role in('capture','toggle'):
   s=state(role);process_state(s,role)
   for k in('current','kernelBound','complete'):s[k]=False
   process_state(s,role,False)
   with self.assertRaises(ValueError):process_state(s,role,True)
 def test_missing_worker_join_or_receipt_refuses(self):
  for k in('workerJoined','receiptVerified','kernelGone','historicalKernelProof','normalExit'):
   s=state();s[k]=False
   with self.subTest(k=k),self.assertRaises(ValueError):process_state(s,'toggle')
 def test_boolean_numeric_metadata_refuses(self):
  for k in('lease','exitCode','nativeWrites','automaticRetries'):
   s=state();s[k]=True if k=='lease'else False
   with self.subTest(k=k),self.assertRaises(ValueError):process_state(s,'toggle')
  for role,k in [('capture','nativeWrites'),('toggle','automaticRetries')]:
   s=state(role);receipt=io.strict(s['stdout']);receipt[k]=False;s['stdout']=json.dumps(receipt)
   with self.subTest(role=role,k=k),self.assertRaises(ValueError):process_state(s,role)
 def test_initial_interpreter_is_not_installed_qs(self):
  # Real own procfs, no pretend QObject/QS or source substitution.
  from materialize import identity
  with self.assertRaises(ValueError):exact_exec(os.getpid(),identity(os.getpid())['start'],{},['/usr/bin/quickshell'])
 def test_constructor_does_not_enter_host(self):
  import candidate_host
  with patch.object(candidate_host.accepted.PrivateHyprSession,'__enter__',side_effect=AssertionError('GUI forbidden')):
   obj=candidate_host.PrivateHyprSession(self.folder/'host',dict(os.environ),1600,1000,b'-- inert CPU source\n')
   self.assertIsNone(obj.host.runtime);self.assertEqual(obj.host.processes,[])
 def test_original_controller_toggle_and_input_episodes_unchanged(self):
  m=load_controller();self.assertEqual(Path(m.__file__),COMPOSITION/'frontend_cases.py');cls=next(n for n in ast.walk(ast.parse(Path(__import__('route_runtime').__file__).read_text()))if isinstance(n,ast.ClassDef)and n.name=='ExactPrivateFrontend');self.assertEqual([n.name for n in cls.body if isinstance(n,ast.FunctionDef)],['open_keyboard'])
 def test_two_by_three_schedule_exact_no_warmup(self):
  self.assertEqual(LIFE_SCHEDULE,(('A',1,'owner','right','pointer'),('A',2,'owner','keyboard','return'),('A',3,'peer','right','pointer'),('B',1,'peer','keyboard','return'),('B',2,'owner','right','pointer'),('B',3,'owner','keyboard','return')))
  self.assertEqual(len(LIFE_SCHEDULE)*2,12)
 def test_selected_fixture_original_methods(self):
  c=native_class();self.assertEqual(c.__module__,'_pin_qs_original_fixture_controller')
  for name in ('launch_legacy','own','capture','focus','scene','close'):self.assertIn(name,c.__dict__)
 def test_root_readonly_functions_exact_ast(self):
  api=original_functions();self.assertEqual(api.observer.__code__.co_filename,str(SOURCE));self.assertEqual(api.transport.__code__.co_filename,str(SOURCE));self.assertFalse(api.transport(['empty']))
if __name__=='__main__':unittest.main()
