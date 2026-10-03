"""Exact normal receipt/nonce/source epoch faults; no QS/GUI on import/run."""
import copy,json,subprocess,tempfile,time,unittest
from pathlib import Path
import terminal_drain as drain
import terminal_qml
NONCE='a'*32
class TerminalDrain(unittest.TestCase):
 def fixture(self):
  records=[dict(event='requested',utcMs=1,kind='snapshot',generation=1,commandDeclaration=['owned','snapshot']),dict(event='started',utcMs=2,kind='snapshot',generation=1,pid=123,commandDeclarationAtStart=['owned','snapshot']),dict(event='exited',utcMs=3,kind='snapshot',generation=1,pid=123,code=0,status=0),dict(event='quiesced',utcMs=4,nonce=NONCE,queuedActions=0)]
  state=dict(screenName='owned-output',currentMonitor=0,nonce=NONCE,quiesced=True,error='',queuedActions=0,queuedBudget=0,timers={k:False for k in ('snapshot','capture','allCapture','captureDelay','queueDelay')},generations={k:int(k=='snapshot')for k in drain.KINDS},current={},processes={k:dict(running=False,pid=None,command=['owned',k])for k in drain.KINDS},records=records)
  return dict(version=1,nonce=NONCE,ack=True,states=[state])
 def validate(self,a,prior=None):return drain.validate(a,NONCE,{'owned-output':0},prior)
 def test_complete_exact_receipts_quiesced_and_no_active_authority(self):self.assertTrue(self.validate(self.fixture()))
 def test_mutable_declarations_retained_without_inferred_kernel_argv(self):
  a=self.fixture();records=a['states'][0]['records'];records[1]['commandDeclarationAtStart']=['owned','next-binding']
  self.assertTrue(self.validate(a));self.assertEqual(records[0]['commandDeclaration'],['owned','snapshot']);self.assertEqual(records[1]['commandDeclarationAtStart'],['owned','next-binding'])
  self.assertNotIn('argv',records[1]);self.assertNotIn('start',records[1])
 def test_malformed_start_declaration_cannot_close_generation(self):
  for declaration in ([],['owned',None],'owned', ['owned','x'*9000]):
   a=self.fixture();a['states'][0]['records'][1]['commandDeclarationAtStart']=declaration
   with self.subTest(declaration=declaration),self.assertRaises(RuntimeError):self.validate(a)
 def test_active_normal_query_is_pending_until_actual_receipt(self):
  a=self.fixture();s=a['states'][0];s['records'].pop(2);s['current']={'snapshot':dict(generation=1,command=['owned','snapshot'],pid=123,started=True)};s['processes']['snapshot'].update(running=True,pid=123)
  self.assertFalse(self.validate(a))
 def test_failed_start_not_running_cannot_infer_normal(self):
  a=self.fixture();s=a['states'][0];s['records']=s['records'][:1]+s['records'][-1:];s['current']={'snapshot':dict(generation=1,command=['owned','snapshot'],pid=0,started=False)}
  with self.assertRaisesRegex(RuntimeError,'live exact current'):self.validate(a)
 def test_actual_exit120_is_failure(self):
  a=self.fixture();a['states'][0]['records'][2]['code']=120
  with self.assertRaisesRegex(RuntimeError,'code/status'):self.validate(a)
 def test_actual_crash_status_is_failure(self):
  a=self.fixture();a['states'][0]['records'][2]['status']=1
  with self.assertRaisesRegex(RuntimeError,'code/status'):self.validate(a)
 def test_missing_or_duplicate_or_wrong_exit_generation_fails(self):
  for change in ('missing','duplicate','generation'):
   a=self.fixture();s=a['states'][0]
   if change=='missing':s['records'].pop(2)
   elif change=='duplicate':s['records'].insert(3,copy.deepcopy(s['records'][2]))
   else:s['records'][2]['generation']=2
   with self.subTest(change=change),self.assertRaises(RuntimeError):self.validate(a)
 def test_nonce_ack_unknown_and_duplicate_key_refuse(self):
  for changes in ({'nonce':'b'*32},{'ack':False},{'extra':True}):
   a=self.fixture();a.update(changes)
   with self.assertRaises(RuntimeError):self.validate(a)
  with self.assertRaises(RuntimeError):json.loads('{"ack":true,"ack":false}',object_pairs_hook=drain.unique)
 def test_output_identity_changes_and_duplicates_refuse(self):
  for kind in ('monitor','missing','duplicate'):
   a=self.fixture()
   if kind=='monitor':a['states'][0]['currentMonitor']=1
   elif kind=='missing':a['states']=[]
   else:a['states'].append(copy.deepcopy(a['states'][0]))
   with self.subTest(kind=kind),self.assertRaises(RuntimeError):self.validate(a)
 def test_epoch_prefix_reset_refuses(self):
  a=self.fixture();prior=copy.deepcopy(a);a['states'][0]['records'][0]['utcMs']=99
  with self.assertRaisesRegex(RuntimeError,'reset or replaced'):self.validate(a,prior)
 def test_new_poll_request_after_quiesce_refuses(self):
  a=self.fixture();s=a['states'][0];s['records'].append(dict(event='requested',utcMs=5,kind='snapshot',generation=2,commandDeclaration=['owned','snapshot']))
  with self.assertRaisesRegex(RuntimeError,'Fresh polling'):self.validate(a)
 def test_old_queued_action_finishes_without_new_budget(self):
  a=self.fixture();s=a['states'][0];s['records'][-1]['queuedActions']=1;s['generations']['action']=1
  s['records']+= [dict(event='requested',utcMs=5,kind='action',generation=1,commandDeclaration=['owned','action']),dict(event='started',utcMs=6,kind='action',generation=1,pid=456,commandDeclarationAtStart=['owned','action']),dict(event='exited',utcMs=7,kind='action',generation=1,pid=456,code=0,status=0)]
  self.assertTrue(self.validate(a));s['records'][-4]['queuedActions']=0
  with self.assertRaisesRegex(RuntimeError,'beyond original'):self.validate(a)
 def test_future_timers_or_orphan_active_process_refuse(self):
  a=self.fixture();a['states'][0]['timers']['snapshot']=True
  with self.assertRaises(RuntimeError):self.validate(a)
  a=self.fixture();a['states'][0]['processes']['capture'].update(running=True,pid=456)
  with self.assertRaisesRegex(RuntimeError,'Unrecorded'):self.validate(a)
 def test_delay_or_queue_still_pending_never_drained(self):
  for kind in ('captureDelay','queueDelay'):
   a=self.fixture();a['states'][0]['timers'][kind]=True;self.assertFalse(self.validate(a))
 def test_qml_inverse_preserves_all_original_feature_handlers(self):
  p=terminal_qml.B/'payload'/terminal_qml.REL;old=p.parents[7]if False else terminal_qml.B.with_name('toolkit-held-matrix-v14')/'payload'/terminal_qml.REL
  self.assertEqual(terminal_qml.reconstruct(p.read_text()),old.read_text());self.assertEqual(terminal_qml.apply(old.read_text()),p.read_text())
 def test_genuine_owned_stdout_drain_preserves_actual_exit_zero(self):
  command=['/usr/bin/python3','-IS','-c','import os,sys;print("ready",file=sys.stderr,flush=True);sys.stdin.read();os.write(1,b"[]\\n")']
  child=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   self.assertEqual(child.stderr.readline().strip(),'ready');child.stdin.close();self.assertEqual(child.stdout.read(),'[]\n');self.assertEqual(child.wait(timeout=2),0)
   # This tests actual unchanged FD output/wait, not actual QS/Qt marker callbacks.
  finally:
   if child.poll()is None:child.kill();child.wait(timeout=2)
   for f in (child.stdin,child.stdout,child.stderr):
    if not f.closed:f.close()

class ServicePhase(unittest.TestCase):
 def setUp(self):
  self.report=dict(processes=[],cleanup={});self.config=dict(queryRoots={})
 def test_exact_observed_absence_does_not_infer_exit_zero(self):
  proof=drain.service_phase(self.config,self.report);self.assertTrue(proof['normalExitNotInferred']);self.assertNotIn('exitCode',proof)
 def test_registered_or_cleanup_without_capture_refuses(self):
  self.config['queryRoots']['service']={'identity':{}}
  with self.assertRaises(RuntimeError):drain.service_phase(self.config,self.report)
  self.config['queryRoots'].clear();self.report['cleanup']['service']={'exitCode':0}
  with self.assertRaises(RuntimeError):drain.service_phase(self.config,self.report)
 def fixture(self,identity):
  self.report.update(processes=[dict(role='held-service',identity=identity)],cleanup={'service':dict(exitCode=0,exactOriginalGone=True)},serviceEvidenceAcceptance=dict(serviceClosed=True,allNormal=True))
  self.config['queryRoots']['service']=dict(identity=identity)
 def test_actual_current_lifetime_refuses_even_claimed_normal(self):
  import helper_observer as observer,os
  self.fixture(observer.process(os.getpid()))
  with self.assertRaisesRegex(RuntimeError,'normal exit and lifetime'):drain.service_phase(self.config,self.report)
 def test_actual_normal_wait_and_kernel_lifetime_gone_accept(self):
  import helper_observer as observer
  child=subprocess.Popen(['/usr/bin/python3','-IS','-c','import sys;print("ready",flush=True);sys.stdin.read()'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
  try:
   self.assertEqual(child.stdout.readline().strip(),'ready');identity=observer.process(child.pid);child.stdin.close();child.wait(timeout=2);self.assertEqual(child.returncode,0);self.fixture(identity);proof=drain.service_phase(self.config,self.report);self.assertEqual(proof['identity'],identity);self.assertTrue(proof['actualOriginalGone'])
   self.report['serviceEvidenceAcceptance']['allNormal']=False
   with self.assertRaisesRegex(RuntimeError,'resource normal closure'):drain.service_phase(self.config,self.report)
   self.report['serviceEvidenceAcceptance']['allNormal']=True;self.report['cleanup']['service']['exitCode']=125
   with self.assertRaisesRegex(RuntimeError,'normal exit'):drain.service_phase(self.config,self.report)
  finally:
   if child.poll()is None:child.kill();child.wait(timeout=2)
   for f in (child.stdin,child.stdout):
    if not f.closed:f.close()
 def test_missing_or_mismatched_registration_is_not_discharge(self):
  self.fixture({'pid':999999,'start':'1','pgid':999999,'parent':1});self.config['queryRoots']['service']['identity']={'pid':999998,'start':'1','pgid':999998,'parent':1}
  with self.assertRaisesRegex(RuntimeError,'root differs'):drain.service_phase(self.config,self.report)
