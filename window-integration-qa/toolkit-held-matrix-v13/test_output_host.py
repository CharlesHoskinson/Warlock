"""Exact selected host inheritance and unchanged launch arguments, no GUI."""
import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import private_output_host as h
B=Path(__file__).resolve().parent;OLD=B.with_name('toolkit-held-matrix-v12')
def selected(name):
 path=B.parent/name/'weston_host.py';spec=importlib.util.spec_from_file_location('_held_host_cpu_'+name.replace('-','_'),path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
class Tests(unittest.TestCase):
 def test_both_actual_host_bodies_and_x11_entry_inherited(self):
  for name in ('private-weston-aq-host-v4','private-weston-x11-host-v2'):
   base=selected(name);api=h.adapt(base)
   self.assertTrue(issubclass(api.ReviewedWestonHost,base.ReviewedWestonHost));self.assertTrue(issubclass(api.PrivateHyprSession,base.PrivateHyprSession));self.assertIs(api.original,base.original)
   for method in ('verify','wait_socket','close','__enter__','__exit__'):self.assertIs(getattr(api.ReviewedWestonHost,method),getattr(base.ReviewedWestonHost,method))
   for method in ('__enter__','guard','ctl','data'):self.assertIs(getattr(api.PrivateHyprSession,method),getattr(base.PrivateHyprSession,method))
   if name=='private-weston-x11-host-v2':self.assertIs(api.PrivateHyprSession.register_x11,base.PrivateHyprSession.register_x11)
 def test_exact_actual_launch_result_env_and_original_deadline(self):
  for name in ('private-weston-aq-host-v4','private-weston-x11-host-v2'):
   base=selected(name);api=h.adapt(base);host=api.ReviewedWestonHost('/tmp/held-cpu-unused',{},1600,1000);command=['/usr/bin/Hyprland','--config','/owned/exact.lua'];env={'actual':'selectors'};proc=SimpleNamespace(pid=321)
   def launch(actual,name,args,environment):
    self.assertIs(actual,host);self.assertEqual(name,'hyprland');self.assertIs(args,command);self.assertIs(environment,env);self.assertNotIn('browserStartupBudget',actual.evidence);return proc
   with patch.object(base.ReviewedWestonHost,'launch',launch),patch.object(h.time,'monotonic',return_value=100.):self.assertIs(host.launch('hyprland',command,env),proc)
   self.assertEqual(host.evidence['browserStartupBudget']['pid'],321);self.assertEqual(host.evidence['browserStartupBudget']['deadlineMonotonic'],115.);self.assertEqual(host.evidence['browserStartupBudget']['launchReturnedMonotonic'],100.)
 def test_other_launch_and_failed_launch_never_add_budget(self):
  base=selected('private-weston-aq-host-v4');api=h.adapt(base);host=api.ReviewedWestonHost('/tmp/held-cpu-unused',{});command=['/usr/bin/dbus-daemon','--session'];env={};proc=SimpleNamespace(pid=321)
  with patch.object(base.ReviewedWestonHost,'launch',return_value=proc) as launch:self.assertIs(host.launch('privateBus',command,env),proc);launch.assert_called_once_with('privateBus',command,env)
  self.assertNotIn('browserStartupBudget',host.evidence)
  with patch.object(base.ReviewedWestonHost,'launch',side_effect=RuntimeError('original refused')),self.assertRaisesRegex(RuntimeError,'original refused'):host.launch('hyprland',[],{})
  self.assertNotIn('browserStartupBudget',host.evidence)
 def test_session_constructor_arguments_and_lua_unchanged(self):
  for name in ('private-weston-aq-host-v4','private-weston-x11-host-v2'):
   base=selected(name);api=h.adapt(base);lua=b'original explicit Lua';env={'HOME':'/owned/exact-home'}
   session=api.PrivateHyprSession('/tmp/held-cpu-unused',env,1600,1000,lua,'pci-exact',True);self.assertIs(session.lua,lua);self.assertEqual(session.host.main_env,dict(env,GSETTINGS_BACKEND='memory'));self.assertEqual(session.host.dri_prime,'pci-exact');self.assertTrue(session.host.mesa_vendor);self.assertIs(session.evidence,session.host.evidence);self.assertIsNone(session.host.runtime)
 def test_collector_exact_browser_source_except_fixed_context_import(self):
  source=(B/'output_readiness.py').read_bytes();expected=(B.parent/'browser-files-flow-v19/output_readiness.py').read_bytes();self.assertEqual(source.replace(b'from private_output_host import original as host_api',b'from private_bus_host import original as host_api'),expected)
  for n in ('output_readiness.qnt','output_readiness_test.qnt'):self.assertEqual((B/n).read_bytes(),(B.parent/'browser-files-flow-v19'/n).read_bytes())
  self.assertNotIn('private_bus_host',(B/'private_output_host.py').read_text());self.assertNotIn('BUS_TEMPLATE',(B/'private_output_host.py').read_text())
 def test_formal_pins_entire_original_runner_before_runtime(self):
  proof=json.loads((B/'output-formal-before-runtime.json').read_text());self.assertEqual(proof['result'],'pass');self.assertFalse(proof['runtimeChanged']);self.assertEqual(proof['sources'][str(B/'run_native.py')],hashlib.sha256((OLD/'run_native.py').read_bytes()).hexdigest())
if __name__=='__main__':unittest.main(verbosity=2)
