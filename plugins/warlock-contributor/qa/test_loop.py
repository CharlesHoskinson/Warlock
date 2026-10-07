"""Guarded coordinator behavior; no native processes or desktop actions."""
import importlib.util,pathlib,shutil,subprocess,unittest
from unittest.mock import patch
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
  self.fixture.start();commands=[]
  def run(command,**kwargs):commands.append(command);return subprocess.CompletedProcess(command,0)
  with patch.object(loop.subprocess,'run',side_effect=run):code=loop.main(['--repo',str(self.repo),'native','--runner','/owned/runner.py','--','--launcher-search'])
  self.assertEqual(code,0);self.assertEqual(len(commands),3)
  self.assertIn('--require-record',commands[0]);self.assertEqual(commands[0],commands[2])
  self.assertIn(str(self.repo/'implementation/elm-build-loop-v1/loop.py'),commands[1]);self.assertEqual(commands[1][-2:],['--','--launcher-search'])
 def test_check_failure_stops_before_native(self):
  with patch.object(loop.subprocess,'run',return_value=subprocess.CompletedProcess([],1)) as run:
   self.assertEqual(loop.main(['--repo',str(self.repo),'native','--runner','/owned/runner.py']),1);self.assertEqual(run.call_count,1)
 def test_failed_postcheck_is_not_hidden_by_successful_native(self):
  results=[subprocess.CompletedProcess([],0),subprocess.CompletedProcess([],0),subprocess.CompletedProcess([],1)]
  with patch.object(loop.subprocess,'run',side_effect=results):self.assertEqual(loop.main(['--repo',str(self.repo),'native','--runner','/owned/runner.py']),1)

if __name__=='__main__':unittest.main()
