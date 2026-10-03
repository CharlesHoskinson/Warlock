"""Actual runner cleanup functions: infrastructure survival and unload guard."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import native_probe_pointer as runner

class CleanupTests(unittest.TestCase):
 def test_failure_stops_only_scenario_before_maintenance(self):
  infrastructure=['bus','compositor','Foot','AX-launcher','AX-registry']
  scenario=['keyboard','actual-device-probe','virtual-pointer','reader','GTK']
  events=[];report={}
  def prepare(env,method):
   self.assertEqual(events,[('finish',p) for p in reversed(scenario)])
   self.assertNotIn(('finish','bus'),events)
   events.append(('prepare',method));return True
  with patch.object(runner,'finish_fixture',side_effect=lambda p:events.append(('finish',p))),patch.object(runner,'manager',side_effect=prepare),patch.object(runner,'ctl',side_effect=lambda *args:events.append(('unload',args[1])) or 'ok'):
   runner.finish_scenario(infrastructure+scenario,len(infrastructure))
   self.assertTrue(runner.retire_private_plugin({},'private.so',report))
  self.assertEqual(events[-2:],[('prepare','PrepareUnload'),('unload','plugin')])
  self.assertEqual(report,{'cleanupUnloadQuiescent':True,'cleanupNormalUnloadResult':'ok'})
 def test_false_quiescence_never_raw_unloads(self):
  report={}
  with patch.object(runner,'manager',return_value=False),patch.object(runner,'ctl') as ctl:
   with self.assertRaisesRegex(RuntimeError,'not quiescent'):runner.retire_private_plugin({},'private.so',report)
   ctl.assert_not_called()
  self.assertEqual(report,{'cleanupUnloadQuiescent':False})
 def test_maintenance_error_is_visible_and_never_unloads(self):
  with patch.object(runner,'manager',side_effect=RuntimeError('bus transport failed')),patch.object(runner,'ctl') as ctl:
   with self.assertRaisesRegex(RuntimeError,'bus transport'):runner.retire_private_plugin({},'private.so',{})
   ctl.assert_not_called()
 def test_actual_finish_fixture_pairs_eof_before_stop(self):
  events=[]
  class Input:
   closed=False
   def close(self):self.closed=True;events.append('paired-real-EOF')
  process=SimpleNamespace(poll=lambda:None,stdin=Input(),wait=lambda timeout:events.append('natural-release-wait'))
  with patch.object(runner,'pid_stop',side_effect=lambda p:events.append('scoped-stop')):runner.finish_fixture(process)
  self.assertEqual(events,['paired-real-EOF','natural-release-wait','scoped-stop'])
 def test_checkpoint_rejects_out_of_range_before_touching_processes(self):
  with patch.object(runner,'finish_fixture') as finish:
   for value in (-1,3):
    with self.assertRaisesRegex(AssertionError,'checkpoint'):runner.finish_scenario(['bus','compositor'],value)
   finish.assert_not_called()
if __name__=='__main__':unittest.main(verbosity=2)
