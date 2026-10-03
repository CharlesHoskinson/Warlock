"""Actual fresh runner/guard/observer contracts; no native process starts."""
import hashlib,json,os,unittest
from pathlib import Path
from unittest.mock import patch
import native_probe_pointer as r
import private_runtime_guard as g
from main_observer import MainObserver
class HostAdaptation(unittest.TestCase):
 def test_fixture_flag_never_mutates_original_environment(self):
  main={'HOME':'/original','WAYLAND_DISPLAY':'main','DBUS_SESSION_BUS_ADDRESS':'main-bus'};original=dict(main)
  private=r.fixture_parent_env(main)
  self.assertEqual(main,original);self.assertEqual(set(private)-set(main),{'HYPR_A11Y_BRIDGE_PRIVATE'});self.assertEqual(private['HYPR_A11Y_BRIDGE_PRIVATE'],'1')
 def test_observer_refuses_dispatch_without_running_any_command(self):
  env=dict(os.environ,HOME='/home/hoskinson',XDG_RUNTIME_DIR='/run/user/'+str(os.getuid()),HYPRLAND_INSTANCE_SIGNATURE='main-signature')
  observer=MainObserver(env)
  with patch.object(observer,'command',side_effect=AssertionError('cannot run')):
   with self.assertRaises(RuntimeError):observer.ctl('dispatch','anything')
 def test_observer_getters_have_explicit_original_target(self):
  env=dict(os.environ,HOME='/home/hoskinson',XDG_RUNTIME_DIR='/run/user/'+str(os.getuid()),HYPRLAND_INSTANCE_SIGNATURE='main-signature')
  observer=MainObserver(env)
  with patch.object(observer,'command',return_value=b'[]') as command:self.assertEqual(observer.data('clients'),[])
  self.assertEqual(command.call_args.args,('/usr/bin/hyprctl','-i','main-signature','-j','clients'))
 def test_private_runtime_scope_failure_precedes_bus_or_wayland(self):
  with patch.object(g.qa,'require_qa_scope',side_effect=RuntimeError('scope')),patch.object(g.qa,'verify_parent',side_effect=AssertionError('no connect')) as peer:
   with self.assertRaisesRegex(RuntimeError,'scope'):g.checked_runtime()
   peer.assert_not_called()
 def test_private_runtime_rejects_foreign_wayland_peer(self):
  runtime=Path('/run/user')/str(os.getuid())/'wqa/abcd';pid=os.getpid();start=Path('/proc/'+str(pid)+'/stat').read_text().rsplit(')',1)[1].split()[19]
  env=dict(XDG_RUNTIME_DIR=str(runtime),DBUS_SESSION_BUS_ADDRESS='unix:path='+str(runtime/'bus'),HYPR_A11Y_BRIDGE_PRIVATE='1',POINTER_QA_COMPOSITOR_PID=str(pid),POINTER_QA_COMPOSITOR_START=start)
  with patch.dict(os.environ,env,clear=True),patch.object(g.qa,'require_qa_scope'),patch.object(g.qa,'verify_runtime',return_value=runtime),patch.object(g.qa,'verify_parent',return_value=dict(pid=pid+1)):
   with self.assertRaisesRegex(RuntimeError,'identity'):g.checked_runtime()
 def test_explicit_signed_orca_prefix_refuses_private_home_substitute(self):
  with patch.dict(os.environ,{'ORCA_QA_READER_ROOT':'/private/home'},clear=True):
   with self.assertRaisesRegex(RuntimeError,'prefix'):g.reader_entry()
 def test_every_prior_pointer_oracle_retained_exactly(self):
  import ast
  source=Path(r.__file__).parent
  prior=source.parent/'pointer-private-host-v3/native-fixture/pointer_cases.py'
  def checks(path):
   return [ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check']
  before,after=checks(prior),checks(source/'native-fixture/pointer_cases.py')
  self.assertGreater(len(before),60)
  for oracle in before:self.assertIn(oracle,after)
  self.assertEqual(hashlib.sha256((source/'native-fixture/popup_geometry.py').read_bytes()).hexdigest(),'ae8098f52e7961ef1035d2c6a800c5d7e0f709c4c6838b12e9c0ceedcefbb76c')
  for name in ['policy_cases.py','lifecycle_cases.py']:
   self.assertEqual((source/'native-fixture'/name).read_bytes(),(source.parent/'pointer-private-host-v3/native-fixture'/name).read_bytes())
 def test_full_policy_and_lifecycle_modules_import_with_real_run(self):
  for name in ('policy_cases.py','lifecycle_cases.py'):
   module=r.load_additional(name);self.assertTrue(callable(module.run));self.assertEqual(Path(module.__file__).parent,Path(r.__file__).parent/'native-fixture')
 def test_private_ipc_has_no_main_fallback(self):
  with patch.object(r,'PRIVATE_SESSION',None),patch.object(r.subprocess,'check_output',side_effect=AssertionError('must not issue IPC')):
   with self.assertRaisesRegex(RuntimeError,'active owned'):r.ctl(dict(os.environ),'clients')
 def test_source_scope_before_main_capture_or_launch(self):
  import inspect
  source=inspect.getsource(r.execute)
  self.assertLess(source.index('qa.require_qa_scope()'),source.index('observer.capture()'))
  self.assertNotIn("ctl(main",source);self.assertNotIn("env=main",source);self.assertNotIn('host_path',source)
 def test_original_files_visibility_is_preserved_without_historical_precondition(self):
  import copy
  for visible in (False,True):
   before={key:None for key in ('clients','focus','cursor','outputs','a11y','reader','files','plugins','keyboards','catalogs','clipboard','configErrors')}
   before.update(clients=[],reader='(<false>,)',files=dict(visible=visible,pid=123,processStart='456',publicSHA256='public',uiSHA256='ui'))
   after=copy.deepcopy(before)
   self.assertTrue(all(MainObserver.compare(before,after).values()))
   after['files']['visible']=not visible
   self.assertFalse(MainObserver.compare(before,after)['originalFilesExactProcessAndCapturedVisibility'])
if __name__=='__main__':unittest.main()
