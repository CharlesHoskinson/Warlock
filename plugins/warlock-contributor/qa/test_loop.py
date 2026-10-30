"""Guarded coordinator behavior; no native processes or desktop actions."""
import importlib.util,pathlib,shutil,subprocess,unittest
from unittest.mock import Mock, patch
import test_warlock as fixtures

ROOT=pathlib.Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('warlock_guarded_loop',ROOT/'docs/warlock-build-loop/v2/loop.py')
loop=importlib.util.module_from_spec(spec);spec.loader.exec_module(loop)

class GuardedLoopTests(unittest.TestCase):
 def setUp(self):
  self.fixture=fixtures.ContributionPolicyTests('test_fresh_start_status_check_record');self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
  self.repo=self.fixture.repo
  destination=self.repo/'plugins/warlock-contributor/scripts/warlock.py';destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(fixtures.CHECKER,destination)
 def test_missing_contract_does_not_run_native(self):
  code=loop.main(['--repo',str(self.repo),'native','--runner','/not/a/native/runner.py'])
  self.assertEqual(code,2)
 def test_valid_contract_allows_explicit_check(self):
  self.fixture.start();self.assertEqual(loop.main(['--repo',str(self.repo),'check']),0)
 def test_native_keeps_serialized_original_launcher_and_checks_afterward(self):
  self.fixture.start();events=[]
  def run(command,**kwargs):events.append(('check',command));return subprocess.CompletedProcess(command,0)
  def native(argv):events.append(('native',argv));return 0
  coordinator=Mock();coordinator.main.side_effect=native
  with patch.object(loop.subprocess,'run',side_effect=run),patch.object(loop,'portable_coordinator',return_value=coordinator) as load:
   code=loop.main(['--repo',str(self.repo),'native','--runner','/owned/runner.py','--','--launcher-search'])
  self.assertEqual(code,0);self.assertEqual([kind for kind,_ in events],['check','native','check'])
  load.assert_called_once_with(self.repo)
  self.assertIn('--require-record',events[0][1]);self.assertEqual(events[0],events[2])
  self.assertEqual(events[1][1],['--repo',str(self.repo),'native','--runner','/owned/runner.py','--','--launcher-search'])
 def test_check_failure_stops_before_native(self):
  with patch.object(loop.subprocess,'run',return_value=subprocess.CompletedProcess([],1)) as run:
   self.assertEqual(loop.main(['--repo',str(self.repo),'native','--runner','/owned/runner.py']),1);self.assertEqual(run.call_count,1)
 def test_failed_postcheck_is_not_hidden_by_successful_native(self):
  results=[subprocess.CompletedProcess([],0),subprocess.CompletedProcess([],1)]
  coordinator=Mock();coordinator.main.return_value=0
  with patch.object(loop.subprocess,'run',side_effect=results),patch.object(loop,'portable_coordinator',return_value=coordinator):
   self.assertEqual(loop.main(['--repo',str(self.repo),'native','--runner','/owned/runner.py']),1)
  coordinator.main.assert_called_once()
 def copy_native_sources(self):
  for relative in loop.PINNED_NATIVE_SOURCES:
   destination=self.repo/relative;destination.parent.mkdir(parents=True,exist_ok=True)
   shutil.copyfile(ROOT/relative,destination)
 def test_portable_coordinator_loads_exact_frozen_sources_without_running_native(self):
  self.copy_native_sources()
  coordinator=loop.portable_coordinator(self.repo)
  self.assertEqual(coordinator.PROTECTED_LAUNCHER,self.repo/'window-integration-qa/qa_run.py')
  self.assertTrue(callable(coordinator.main))
 def test_portable_coordinator_refuses_changed_source_before_loading(self):
  self.copy_native_sources()
  source=self.repo/'window-integration-qa/qa_launch.py';source.write_bytes(source.read_bytes()+b'\n')
  with self.assertRaisesRegex(ValueError,'Pinned native source changed'):
   loop.portable_coordinator(self.repo)
 def test_portable_coordinator_refuses_symlink_source(self):
  self.copy_native_sources()
  source=self.repo/'window-integration-qa/qa_launch.py';source.unlink();source.symlink_to(ROOT/'window-integration-qa/qa_launch.py')
  with self.assertRaisesRegex(ValueError,'Native source symlink refused'):
   loop.portable_coordinator(self.repo)

if __name__=='__main__':unittest.main()
