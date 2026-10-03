import json,unittest
from maintenance import *
class Tests(unittest.TestCase):
 def fixture(self,ready=True):
  identity=Identity('abc_1_2',123,456,7,8)
  artifact=dict(nativeAccepted=True,productionAccepted=True,privateProbeAbsent=True,sha256='a'*64,packageID='reviewed-v1',library=os.path.expanduser('~/.local/lib/omarchy-a11y-reviewed-v1.so'))
  calls=[];current=[identity]
  def transport(command,env):
   calls.append(command);self.assertEqual(env['HYPRLAND_INSTANCE_SIGNATURE'],identity.signature);self.assertEqual(command[:3],['hyprctl','-i',identity.signature])
   if command[3]=='repl':return json.dumps(dict(instance=identity.signature,packageID=artifact['packageID'],ready=ready))
   return 'ok'
  manager=Maintenance(identity,artifact,lambda:current[0],lambda row:None,transport)
  return manager,calls,current
 def test_strict_preferred_no_fallback(self):
  with self.assertRaises(Refused):resolve([{'instance':'other'}],environment='missing')
 def test_ambiguous_missing_environment(self):
  with self.assertRaises(Refused):resolve([{'instance':'a'},{'instance':'b'}])
 def test_unique_missing_environment(self):self.assertEqual(resolve([{'instance':'a'}])['instance'],'a')
 def test_explicit_target_wins_environment(self):self.assertEqual(resolve([{'instance':'a'},{'instance':'b'}],explicit='b',environment='a')['instance'],'b')
 def test_unapproved_manifest_refused(self):
  with self.assertRaises(Refused):approved_manifest(dict(nativeAccepted=False))
 def test_false_prepare_never_unloads(self):
  manager,calls,_=self.fixture(False)
  with self.assertRaises(Refused):manager.unload()
  self.assertEqual(len(calls),2);self.assertFalse(any('unload' in c for c in calls))
 def test_true_prepare_exact_normal_unload(self):
  manager,calls,_=self.fixture();manager.unload();self.assertEqual(calls[-1][3:5],['plugin','unload'])
 def test_target_drift_before_prepare_refused(self):
  manager,calls,current=self.fixture();old=manager.transport
  def change(command,env):
   result=old(command,env);current[0]=Identity('abc_1_2',123,999,7,8);return result
  manager.transport=change
  with self.assertRaises(Refused):manager.unload()
  self.assertEqual(len(calls),1)
 def test_socket_drift_after_prepare_never_unloads(self):
  manager,calls,current=self.fixture();old=manager.transport
  def change(command,env):
   result=old(command,env)
   if 'prepare_unload' in command[-1]:current[0]=Identity('abc_1_2',123,456,7,999)
   return result
  manager.transport=change
  with self.assertRaises(Refused):manager.unload()
  self.assertEqual(len(calls),2)
 def test_transport_failure_never_unloads(self):
  manager,calls,_=self.fixture();old=manager.transport
  def fail(command,env):
   if 'prepare_unload' in command[-1]:raise OSError('lost socket')
   return old(command,env)
  manager.transport=fail
  with self.assertRaises(OSError):manager.unload()
  self.assertEqual(len(calls),1)
if __name__=='__main__':unittest.main()
