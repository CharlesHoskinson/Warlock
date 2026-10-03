"""Arm current-boundary faults; fake native dispatch, actual owned source checks."""
import copy,json,os,tempfile,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import helper_observer as observer,helper_setup,evaluation_setup as setup
import test_evaluations as fixture
class ArmPublication(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.config,_,_=fixture.EvaluationProtocol().fixture(self.root,'reload')
  self.config.update(helpers={'snap':{'wrapper':str(self.root/'entry'),'actual':str(self.root/'actual')},'shell':{'wrapper':str(self.root/'shell'),'actual':str(self.root/'shellactual')}},log=str(self.root/'journal'),allowed=[])
  Path(self.config['log']).touch(mode=0o600);self.path=self.root/'config';helper_setup.write_json(self.path,self.config);self.controls=[]
  def ctl(*args):
   self.controls.append(args)
   if 'print(table.concat' in args[1]:
    ticket=self.config['evaluationTickets'][-1];return '\n'.join([ticket['nonce'],ticket['kind'],str(ticket['count']),'0'])
   return ''
  self.evaluation=setup.Evaluations({'WINDOW_QA_HELPER_CONFIG':str(self.path)},self.config,SimpleNamespace(guard=lambda:None,ctl=ctl),self.root,{})
  self.patchers=[patch.object(setup,'ipc_until',side_effect=lambda config,deadline:copy.deepcopy(config['evaluationTickets'][0]['armIPC'])),patch.object(setup,'pending_helper_processes',return_value=[])]
  for p in self.patchers:p.start()
 def tearDown(self):
  for p in reversed(self.patchers):p.stop()
  self.temp.cleanup()
 def evidence(self):return json.loads(Path(self.evaluation.report['evaluationArmDiagnostics'][-1]).read_text())
 def rows(self,items):Path(self.config['log']).write_text(''.join(json.dumps(row)+'\n'for row in items))
 def test_quiet_single_publication_original_budget_and_dispatch(self):
  ticket=self.evaluation.arm('reload',['reload']);self.assertEqual(ticket['serial'],2);self.assertEqual(len(self.config['evaluationTickets']),2);self.assertEqual(len(self.controls),2);self.assertTrue(self.evidence()['accepted']);self.assertEqual(self.evidence()['budgetSeconds'],8)
 def test_spawned_pending_releases_then_retries_without_budget_reset(self):
  calls=[0]
  def pending(*_):
   calls[0]+=1;return [{'identity':{'pid':123,'start':'fixture only'},'argv':['fixture']}]if calls[0]==2 else []
  with patch.object(setup,'pending_helper_processes',side_effect=pending):self.evaluation.arm('reload',['reload'])
  e=self.evidence();self.assertTrue(any(row.get('exactPendingProcesses')for row in e['attempts']));self.assertEqual(len([row for row in e['attempts']if row['stage']=='published']),1);self.assertEqual(e['deadline'],self.evidence()['deadline'])
 def test_configuration_changed_during_source_guard_is_hard_refusal(self):
  real=observer.evaluation_operation
  def mutate(*args):
   result=real(*args);new=copy.deepcopy(self.config);new['instance']='changed';helper_setup.write_json(self.path,new);return result
  with patch.object(observer,'evaluation_operation',side_effect=mutate),self.assertRaisesRegex(RuntimeError,'configuration changed during arm'):self.evaluation.arm('reload',['reload'])
  self.assertFalse(self.evidence()['accepted']);self.assertTrue(any(row.get('configChanged')for row in self.evidence()['attempts']));self.assertEqual(self.controls,[])
 def test_unknown_source_authority_is_hard_refusal(self):
  with patch.object(observer,'evaluation_operation',side_effect=RuntimeError('actual source refusal')),self.assertRaisesRegex(RuntimeError,'actual source refusal'):self.evaluation.arm('reload',['reload'])
  self.assertFalse(self.evidence()['atomicReplaceOccurred']);self.assertEqual(len(self.config['evaluationTickets']),1)
 def test_nonzero_completed_helper_refuses_even_another_is_pending(self):
  one=dict(event='started',operation='one',wrapper=dict(pid=1,start='1'),delegate=dict(pid=2,start='1'));two=dict(one,operation='two')
  self.rows([one,two,dict(one,event='terminal',exitCode=120)])
  with self.assertRaisesRegex(RuntimeError,'terminal mismatch'):self.evaluation.arm('reload',['reload'])
  self.assertEqual(self.controls,[]);self.assertIn('terminalError',self.evidence()['attempts'][-1])
 def test_malformed_rows_do_not_get_retry_authority(self):
  self.rows([dict(event='unknown')])
  with self.assertRaisesRegex(RuntimeError,'Unknown helper event'):self.evaluation.arm('reload',['reload'])
  self.assertFalse(self.evidence()['atomicReplaceOccurred'])
 def test_feature_refusal_is_not_normalized(self):
  self.rows([dict(event='refused',operation='fixture')])
  with self.assertRaisesRegex(RuntimeError,'forbids feature'):self.evaluation.arm('reload',['reload'])
  self.assertFalse(self.evidence()['accepted'])
 def test_expiry_during_guard_forbids_publication(self):
  real=setup.remaining;expired=[False]
  def remaining(deadline):
   if expired[0]:raise TimeoutError('Original evaluation arm deadline expired')
   return real(deadline)
  def expire(*_):expired[0]=True;return 'fixture authority'
  with patch.object(setup,'remaining',side_effect=remaining),patch.object(observer,'evaluation_operation',side_effect=expire),self.assertRaises(TimeoutError):self.evaluation.arm('reload',['reload'])
  self.assertFalse(self.evidence()['atomicReplaceOccurred']);self.assertEqual(self.controls,[])
 def test_atomic_replace_late_observation_cannot_dispatch(self):
  def late(path,value,deadline,evidence):
   helper_setup.write_json(path,value);evidence['atomicReplaceOccurred']=True;raise TimeoutError('late atomic replace observation')
  with patch.object(setup,'publish_until',side_effect=late),self.assertRaises(TimeoutError):self.evaluation.arm('reload',['reload'])
  e=self.evidence();self.assertTrue(e['atomicReplaceOccurred']);self.assertFalse(e['accepted']);self.assertEqual(self.controls,[]);self.assertIsNone(self.evaluation.current)
 def test_exclusive_diagnostic_permissions(self):
  self.evaluation.arm('reload',['reload']);path=Path(self.evaluation.report['evaluationArmDiagnostics'][0]);self.assertEqual(path.stat().st_mode&0o777,0o600);self.assertIn('eventSnapshots',self.evidence())
