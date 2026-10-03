"""Actual controller/manager CPU replay; renderer/native fixtures are explicit."""
import copy,os,tempfile,threading,time,unittest
from pathlib import Path
from scene_manager import SceneManager
from scene_controller import ids,key
from test_scene_controller import Desktop,Transport

class Tests(unittest.TestCase):
 def setUp(self):
  self.d=Desktop();self.t=Transport();self.m=SceneManager(lambda number:(self.d,self.t));self.tmp=tempfile.TemporaryDirectory()
 def tearDown(self):
  if self.d.block:self.d.block.set()
  for a in self.m.actors+self.m.retiring:a.controller.workers.shutdown(wait=True,cancel_futures=True)
  self.tmp.cleanup()
 def wait(self,predicate):
  end=time.monotonic()+2
  while time.monotonic()<end:
   if predicate():return
   time.sleep(.002)
  self.fail('Actual CPU controller did not reach expected boundary')
 def request(self,command='minimize',context='exact-context'):
  w=self.d.windows[0];return self.m.request(command,w['address'],w['stableId'],w['pid'],context=context)
 def reserve(self,command='restore'):
  w=self.d.windows[0];return self.m.reserve(command,w['address'],w['stableId'],w['pid'])
 def event(self,r,kind='ready'):
  return self.c.event({'event':kind,'token':r.token,'identities':ids(r.members),'servicePromoted':True,'sourceDigests':[{k:s[k] for k in ('stableId','pid','digest')}for s in r.sources]})
 def moving(self,pending=False):
  reply=self.request();self.c=self.m.actors[0].controller
  self.wait(lambda:any(v['command']=='validate' and v['token']==reply['token']for v in self.t.sent));old=self.c.current;self.assertTrue(self.event(old));self.assertEqual(len(self.d.commits),3)
  self.d.block=threading.Event();self.d.started.clear();reserved=self.reserve()
  if not pending:self.m.activate(reserved['receipt'],context='exact-context');self.assertTrue(self.d.started.wait(1))
  r=self.c.current;self.assertFalse(r.validated);self.assertTrue(r.visual);self.assertEqual(r.sources,old.sources)
  self.d.reduced_flag=True;self.m.watchdog();self.assertIsNotNone(r.retirement);self.assertEqual(self.cancel_count(),1)
  return r,reserved
 def cancel_count(self):return sum(v['command']=='cancel'for v in self.t.sent)
 def pending_visual(self):
  reply=self.request();self.c=self.m.actors[0].controller
  self.wait(lambda:any(v['command']=='validate' and v['token']==reply['token']for v in self.t.sent));self.assertTrue(self.event(self.c.current));reserved=self.reserve();return self.c.current,reserved
 def observe_in_thread(self,target,observed=True):
  entered=threading.Event();release=threading.Event();answers=[];errors=[]
  def reduced():
   entered.set()
   if not release.wait(2):raise TimeoutError('exact CPU reduction observation boundary')
   return observed
  self.d.reduced=reduced
  def run():
   try:answers.append(target())
   except Exception as error:errors.append(error)
  worker=threading.Thread(target=run);worker.start();self.assertTrue(entered.wait(1));return worker,release,answers,errors
 def test_stale_pending_watchdog_observation_cannot_cancel_new_receipt(self):
  old,_=self.pending_visual();worker,release,answers,errors=self.observe_in_thread(self.m.watchdog)
  done=threading.Event();new=[]
  def reserve():new.append(self.reserve('minimize'));done.set()
  request=threading.Thread(target=reserve);request.start()
  try:
   self.assertTrue(done.wait(.15),'accepted successor blocked behind read-only setting observation');successor=self.c.current;self.assertIsNot(successor,old)
   release.set();worker.join(1);request.join(1);self.assertFalse(errors);self.assertFalse(worker.is_alive());self.assertIs(self.c.current,successor);self.assertEqual(successor.profile['managerReceipt'],new[0]['receipt']);self.assertIsNone(successor.retirement);self.assertEqual(self.cancel_count(),0);self.assertFalse(old.validated);self.assertEqual(self.d.released,[])
  finally:release.set();worker.join(2);request.join(2);self.d.reduced=lambda:self.d.reduced_flag
 def test_current_pending_observed_true_then_off_retires_and_freshly_seeds(self):
  old,reply=self.pending_visual();received=old.profile['receivedNs'];worker,release,answers,errors=self.observe_in_thread(self.m.watchdog)
  try:
   self.d.reduced_flag=False;release.set();worker.join(1);self.assertFalse(errors);self.assertFalse(worker.is_alive());self.assertIsNotNone(old.retirement);self.assertEqual(self.cancel_count(),1);self.assertEqual(self.d.released,[])
   self.assertTrue(self.ack(old));fresh=self.c.current;self.assertIsNot(fresh,old);self.assertTrue(fresh.profile['contextPending']);self.assertEqual(fresh.profile['receivedNs'],received);self.assertEqual(fresh.profile['managerReceipt'],reply['receipt']);self.assertEqual(len(self.d.commits),3)
   self.d.reduced=lambda:self.d.reduced_flag;self.m.activate(reply['receipt'],context='fresh-current-context');self.wait(lambda:any(v['command']=='seed' and v['token']==fresh.token for v in self.t.sent));self.assertTrue(fresh.validated);self.assertEqual(self.d.captures,6);self.assertEqual(len(self.d.commits),3);self.assertFalse(self.event(old,'endpoint'))
  finally:release.set();worker.join(2);self.d.reduced=lambda:self.d.reduced_flag
 def test_stale_prepare_observation_cannot_retire_or_validate_successor(self):
  old,reply=self.pending_visual();self.d.block=threading.Event();self.d.started.clear();self.m.activate(reply['receipt'],context='exact-context');self.assertTrue(self.d.started.wait(1))
  worker,release,answers,errors=self.observe_in_thread(lambda:self.c.prepare_allowed(old))
  done=threading.Event();new=[]
  def reserve():new.append(self.reserve('minimize'));done.set()
  request=threading.Thread(target=reserve);request.start()
  try:
   self.assertTrue(done.wait(.15),'accepted successor blocked behind prepare setting observation');successor=self.c.current;release.set();worker.join(1);request.join(1);self.assertFalse(errors);self.assertEqual(answers,[False]);self.assertIsNone(successor.retirement);self.assertEqual(successor.profile['managerReceipt'],new[0]['receipt']);self.assertEqual(self.cancel_count(),0);self.assertFalse(old.validated);self.assertFalse(successor.validated);self.assertEqual(len(self.d.commits),3)
  finally:release.set();worker.join(2);request.join(2);self.d.reduced=lambda:self.d.reduced_flag;self.d.block.set()
 def ack(self,r,**overrides):
  e={'event':'cancelled','token':r.retirement.token,'identities':ids(r.retirement.members)};e.update(overrides);return self.c.event(e)
 def finish_fresh(self):
  self.d.block.set();self.wait(lambda:self.c.current is None)
 def test_original_actual_blocked_initial_receipt_survives_reduction(self):
  self.d.block=threading.Event();reply=self.request();self.c=self.m.actors[0].controller;self.assertTrue(self.d.started.wait(1));r=self.c.current;received=r.profile['receivedNs'];self.d.reduced_flag=True
  self.m.watchdog();self.assertIs(self.c.current,r);self.assertFalse(r.validated);self.assertEqual(r.profile['receivedNs'],received);self.assertEqual(self.d.commits,[]);self.assertEqual(self.t.sent,[])
  self.finish_fresh();self.assertEqual([v[0]for v in self.d.commits],['minimize']*3);self.assertEqual(self.c.history[-1].profile['managerReceipt'],reply['receipt']);self.assertNotIn('failure',r.profile)
 def test_exact_ack_creates_fresh_object_token_and_no_old_fallback(self):
  r,receipt=self.moving();binding=r.retirement;received=r.profile['receivedNs'];before=list(self.d.commits);self.assertEqual(self.d.released,[])
  self.assertTrue(self.ack(r));fresh=self.c.current;self.assertIsNot(fresh,r);self.assertNotEqual(fresh.token,r.token);self.assertEqual(fresh.profile['receivedNs'],received);self.assertEqual(fresh.profile['managerReceipt'],receipt['receipt']);self.assertFalse(fresh.validated);self.assertIsNone(fresh.accepted_operation);self.assertEqual(fresh.sources,[]);self.assertIsNone(fresh.previous);self.assertEqual(self.d.commits,before);self.assertEqual(self.d.released[-1],binding.sources)
  self.finish_fresh();self.assertEqual([v[0]for v in self.d.commits],['minimize']*3+['restore']*3);self.assertFalse(self.event(r,'endpoint'));self.assertFalse(self.ack(r))
 def test_wrong_token_order_missing_or_ready_endpoint_cannot_ack(self):
  r,_=self.moving()
  for change in ({'token':r.previous.token},{'identities':ids(r.members)[::-1]},{'identities':ids(r.members)[:-1]},{'event':'endpoint'},{'event':'ready'}):
   self.assertFalse(self.ack(r,**change));self.assertIs(self.c.current,r);self.assertEqual(self.d.released,[]);self.assertEqual(len(self.d.commits),3)
 def test_pending_context_rebinds_exact_ingress_object_and_token(self):
  r,reply=self.moving(pending=True);received=r.profile['receivedNs'];ingress=self.m.pending[reply['receipt']];self.assertIs(ingress['provisional'],r)
  self.assertTrue(self.ack(r));fresh=self.c.current;self.assertTrue(fresh.profile['contextPending']);self.assertEqual(fresh.profile['receivedNs'],received);self.assertIs(ingress['provisional'],fresh);self.assertEqual(ingress['provisionalToken'],fresh.token);self.assertEqual(len(self.d.commits),3)
  self.m.activate(reply['receipt'],context='fresh-exact-context');self.assertEqual(fresh.context,'fresh-exact-context');self.finish_fresh();self.assertEqual([v[0]for v in self.d.commits[-3:]],['restore']*3)
 def test_context_accepted_during_retirement_requires_fresh_validation(self):
  r,reply=self.moving(pending=True);self.m.activate(reply['receipt'],context='new-context');self.assertFalse(r.profile['contextPending']);self.assertEqual(r.context,'new-context');self.assertFalse(r.validated);self.assertEqual(len(self.d.commits),3)
  self.assertTrue(self.ack(r));fresh=self.c.current;self.assertEqual(fresh.context,'new-context');self.assertFalse(fresh.validated);self.finish_fresh();self.assertEqual(self.c.history[-1].context,'new-context')
 def test_successor_keeps_old_binding_one_cancel_and_latest_receipt(self):
  r,_=self.moving();binding=r.retirement;retargets=sum(v['command']=='retarget'for v in self.t.sent);new=self.reserve('minimize');successor=self.c.current
  self.assertIs(successor.retirement,binding);self.assertEqual(self.cancel_count(),1);self.assertEqual(sum(v['command']=='retarget'for v in self.t.sent),retargets);self.assertFalse(self.m.activate(new['receipt'],context='latest')['completed'])
  self.assertTrue(self.ack(successor));fresh=self.c.current;self.assertEqual(fresh.profile['managerReceipt'],new['receipt']);self.assertEqual(fresh.profile['ingressCommand'],'minimize');self.finish_fresh();self.assertEqual(self.c.history[-1].operation,'minimize');self.assertFalse(any(v[0]=='restore'for v in self.d.commits))
 def test_relative_successor_is_registered_without_retargeting_retirement(self):
  r,_=self.moving();new=self.reserve('activate');successor=self.c.current;self.assertIs(successor.retirement,r.retirement);self.assertEqual(successor.profile['ingressCommand'],'activate');self.assertEqual(self.m.pending[new['receipt']]['provisionalToken'],successor.token);self.assertEqual(self.cancel_count(),1)
 def test_reduction_off_cannot_revive_old_token_but_fresh_scene_can_seed(self):
  r,_=self.moving();self.d.reduced_flag=False;self.m.watchdog();self.assertEqual(self.cancel_count(),1);self.assertIs(self.c.current,r);self.assertEqual(self.d.captures,3)
  self.assertTrue(self.ack(r));fresh=self.c.current;self.d.block.set();self.wait(lambda:any(v['command']=='seed' and v['token']==fresh.token for v in self.t.sent));self.assertTrue(fresh.validated);self.assertEqual(self.d.captures,6);self.assertEqual(len(self.d.commits),3);self.assertFalse(self.event(r,'ready'));self.assertFalse(self.event(r,'endpoint'))
 def test_old_worker_observation_cannot_validate_or_commit_new_scene(self):
  r,_=self.moving();self.assertTrue(self.ack(r));fresh=self.c.current;self.assertFalse(r.validated);self.assertIs(self.c.current,fresh);self.assertEqual(len(self.d.commits),3);self.finish_fresh();self.assertFalse(r.validated);self.assertEqual(len(self.d.commits),6)
 def test_queue_failure_after_actual_send_latches_quarantine_and_no_retry(self):
  reply=self.request();self.c=self.m.actors[0].controller;self.wait(lambda:any(v['command']=='validate'for v in self.t.sent));self.assertTrue(self.event(self.c.current));self.d.block=threading.Event();self.d.started.clear();self.request('restore');self.assertTrue(self.d.started.wait(1));r=self.c.current;send=self.t.send
  def broken(message):
   send(message)
   if message['command']=='cancel':raise BrokenPipeError('unknown after actual submission')
  self.t.send=broken;self.d.reduced_flag=True;self.m.watchdog();self.assertTrue(r.retirement.uncertain);self.assertFalse(r.retirement.queued);self.assertEqual(self.cancel_count(),1);self.m.watchdog();self.assertEqual(self.cancel_count(),1);self.assertFalse(self.ack(r));self.assertEqual(self.d.released,[]);self.assertEqual(len(self.d.commits),3)
  with self.assertRaisesRegex(RuntimeError,'uncertain'):self.c.close()
 def test_real_filesystem_reservation_failure_retains_resources_and_no_send(self):
  r,_=self.moving();# exercise a second binding epoch with a real failing journal path
  self.assertTrue(self.ack(r));self.finish_fresh();self.d.reduced_flag=False;self.d.block=None;reply=self.request('minimize');self.wait(lambda:any(v['command']=='validate' and v['token']==reply['token']for v in self.t.sent));self.assertTrue(self.event(self.c.current));self.d.block=threading.Event();self.d.started.clear();self.request('restore');self.assertTrue(self.d.started.wait(1));r=self.c.current
  path=Path(self.tmp.name)/'missing-parent'/'journal'
  def journal(value):
   if value and value['profile'].get('visualRetirement'):path.write_text('durable reservation')
  self.c.journal=journal;before=self.cancel_count();self.d.reduced_flag=True;self.m.watchdog();self.assertTrue(r.retirement.uncertain);self.assertFalse(r.retirement.attempted);self.assertEqual(self.cancel_count(),before);self.assertEqual(r.profile['visualRetirement']['sources'],r.sources);self.assertIn('No such file',r.profile['visualRetirementFailure'])
 def test_actual_ack_journal_failure_precedes_capture_disposal(self):
  r,_=self.moving();path=Path(self.tmp.name)/'missing-parent'/'ack'
  def journal(value):
   if value and value['profile'].get('visualRetirementAckNs'):path.write_text('ack')
  self.c.journal=journal;self.assertFalse(self.ack(r));self.assertTrue(r.retirement.uncertain);self.assertTrue(r.retirement.acknowledged);self.assertIs(self.c.current,r);self.assertEqual(self.d.released,[]);self.assertEqual(len(self.d.commits),3)
 def test_post_ack_replacement_persistence_failure_blocks_fresh_worker(self):
  r,_=self.moving();path=Path(self.tmp.name)/'missing-parent'/'fresh'
  def journal(value):
   if value and value['profile'].get('visualRetirementFreshToken'):path.write_text('fresh')
  self.c.journal=journal;self.assertFalse(self.ack(r));fresh=self.c.current;self.assertIsNot(fresh,r);self.assertTrue(fresh.retirement.uncertain);self.assertFalse(fresh.validated);self.d.block.set();self.c.workers.shutdown(wait=True);self.assertEqual(len(self.d.commits),3)
 def test_transport_failure_latches_even_after_genuine_cancel_ack(self):
  r,_=self.moving();self.c.transport_failure('owned stream failure');self.assertTrue(r.retirement.uncertain);self.assertFalse(self.ack(r));self.assertIs(self.c.current,r);self.assertEqual(self.d.released,[]);new=self.reserve('restore');self.assertTrue(self.c.current.retirement.uncertain);self.m.activate(new['receipt'],context='later');self.assertFalse(self.c.current.validated);self.assertEqual(self.cancel_count(),1)
 def test_changed_source_or_channel_refuses_before_disposal(self):
  r,_=self.moving();r.sources[0]['digest']='f'*64;self.assertFalse(self.ack(r));self.assertTrue(r.retirement.uncertain);self.assertEqual(self.d.released,[]);self.assertEqual(len(self.d.commits),3)
 def test_explicit_deadline_terminates_receipt_but_still_requires_visual_ack(self):
  r,_=self.moving();r.profile['receivedNs']=time.monotonic_ns()-2100000000;self.m.watchdog();self.assertEqual(r.profile['requestTerminated'],'controller deadline');self.assertIs(self.c.current,r);self.assertEqual(self.d.released,[]);self.assertTrue(self.ack(r));self.assertIsNone(self.c.current);self.assertEqual(len(self.d.commits),3)
 def test_context_failure_keeps_binding_and_capture_until_ack(self):
  r,reply=self.moving(pending=True);self.assertTrue(self.m.fail_ingress(reply['receipt'],'definite context refusal'));self.assertIs(self.c.current,r);self.assertEqual(self.d.released,[]);self.assertTrue(self.ack(r));self.assertIsNone(self.c.current);self.assertEqual(len(self.d.commits),3)
 def test_cancel_persistence_order_and_exact_old_command_payload(self):
  journal=[];send=self.t.send
  def logsend(value):journal.append(('send',copy.deepcopy(value)));send(value)
  self.t.send=logsend;self.m.options['journal']=lambda value:journal.append(('journal',copy.deepcopy(value)))
  r,_=self.moving();index=next(i for i,row in enumerate(journal)if row[0]=='send'and row[1]['command']=='cancel');before=journal[index-1];self.assertEqual(before[0],'journal');self.assertEqual(before[1]['profile']['visualRetirement']['token'],r.retirement.token);self.assertFalse(before[1]['profile']['visualRetirement']['attempted']);self.assertEqual(journal[index][1],{'command':'cancel','token':r.retirement.token,'identities':ids(r.members)})
if __name__=='__main__':unittest.main(verbosity=2)
