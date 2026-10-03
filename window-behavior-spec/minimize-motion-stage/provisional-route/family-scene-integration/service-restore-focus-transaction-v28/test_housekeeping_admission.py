"""Genuine Unix-peer/journal/receipt-lock scheduling; CPU native effects only."""
from copy import deepcopy
import hashlib,json,os
from pathlib import Path
import sys,threading,time,types,unittest
from unittest.mock import patch
import test_readonly_ipc as ipc_fixture
import test_scene_controller as scene_fixture
from native_runtime import NativeFactory
from owned_commands import OwnedCommands
from snapshot_cache import SnapshotCache
from service_runtime import RuntimeService,JournalStore

EVIDENCE=[]
EXPECTED=['j/clients','/repl print(hl.plugin.hyprbars.window_families())','j/clients']
class NoHelper:
 def register(self,*a,**kw):raise AssertionError('housekeeping must not execute any helper')
class AdmissionKernelTests(unittest.TestCase):
 def setUp(self):
  self.ipc=ipc_fixture.ReadonlyKernelTests();self.ipc.setUp();self.scene=None;self.threads=[];self.releases=[];self.data=[]
  self.ipc.handler=lambda c,d:(self.data.append(d.decode('ascii')),c.sendall(b'[]'))
  f=self.factory=NativeFactory.__new__(NativeFactory);f.guard=self.ipc.guard;f.readonly=self.ipc.reader;f.journal_lock=self.ipc.lock;f.keeper=NoHelper();f.housekeeping_commands=OwnedCommands(f.keeper,self.ipc.env,readonly=f.readonly)
  f.shared_cache=SnapshotCache(self.ipc.root/'cache',lambda *_:(_ for _ in()).throw(AssertionError('empty cache')),session=self.ipc.session)
 def tearDown(self):
  for e in self.releases:e.set()
  if self.scene and self.scene.d.commit_block:self.scene.d.commit_block.set()
  for t in self.threads:t.join(3);self.assertFalse(t.is_alive(),'selected CPU worker did not terminate')
  if self.scene:self.scene.tearDown()
  self.ipc.tearDown()
 def launch(self,fn):
  errors=[]
  def run():
   try:fn()
   except BaseException as e:errors.append(e)
  t=threading.Thread(target=run);self.threads.append(t);t.start();return t,errors
 def real_scene(self):
  self.scene=scene_fixture.SceneTests();self.scene.setUp();self.scene.c.lock=self.ipc.lock;return self.scene.seed()
 def closed(self,n,reply_sizes=None):
  rows=self.ipc.reader.snapshot()['history'];self.assertEqual(len(rows),n)
  for index,r in enumerate(rows):
   self.assertIs(r['closed'],True);self.assertIs(r['published'],True)
   if r['outcome']=='complete':self.assertTrue(r['evidence']['completeServerEOF']);self.assertEqual(r['evidence']['peer']['pid'],os.getpid());self.assertEqual(r['evidence']['replyBytes'],2 if reply_sizes is None else reply_sizes[index])
  self.assertEqual(self.ipc.store.read()['readonlyOwnership'],self.ipc.reader.snapshot());return deepcopy(rows)
 def assert_unlock(self):
  acquired=threading.Event()
  def probe():
   with self.ipc.lock:acquired.set()
  t,e=self.launch(probe);self.assertTrue(acquired.wait(1));t.join(1);self.assertFalse(e)
 def test_healthy_actual_three_fixed_queries_durable_peer_eof_and_latency(self):
  start=time.monotonic_ns();self.factory.housekeep();end=time.monotonic_ns();self.assertEqual(self.data,EXPECTED);rows=self.closed(3);self.assertTrue(all(r['outcome']=='complete'for r in rows));self.assert_unlock()
  EVIDENCE.append({'case':'healthy','totalMs':(end-start)/1e6,'registeredToFinishedMs':[(r['finishedNs']-r['registeredNs'])/1e6 for r in rows],'rows':rows})
 def test_actual_ready_commit_admission_wait_does_not_start_query_budget(self):
  record=self.real_scene();self.scene.d.commit_block=threading.Event();self.releases.append(self.scene.d.commit_block);self.scene.d.started.clear()
  commit,ce=self.launch(lambda:self.scene.event(record,'ready'));self.assertTrue(self.scene.d.started.wait(2));before=len(self.ipc.reader.rows);begun=threading.Event();start=time.monotonic_ns()
  def query():begun.set();self.factory.housekeep()
  worker,we=self.launch(query);self.assertTrue(begun.wait(1));self.assertFalse(worker.join(.72));self.assertTrue(worker.is_alive());self.assertEqual(len(self.ipc.reader.rows),before);self.assertEqual(self.data,[])
  release=time.monotonic_ns();self.scene.d.commit_block.set();commit.join(3);worker.join(3);self.assertFalse(ce);self.assertFalse(we);self.assertEqual(len(record.results),3);rows=self.closed(3);self.assertTrue(all(r['registeredNs']>=release and r['outcome']=='complete'for r in rows));self.assertEqual(self.data,EXPECTED)
  EVIDENCE.append({'case':'actual-ready-before-admission','admissionWaitMs':(release-start)/1e6,'releaseNs':release,'rows':rows,'cpuCommitResults':record.results,'nativeEffectsFixture':True})
 def test_actual_ready_commit_cannot_enter_after_query_send_before_eof(self):
  record=self.real_scene();seen=threading.Event();permit=threading.Event();self.releases.append(permit)
  def reply(c,d):
   self.data.append(d.decode('ascii'))
   if len(self.data)==1:seen.set();self.assertTrue(permit.wait(2))
   c.sendall(b'[]')
  self.ipc.handler=reply;worker,we=self.launch(self.factory.housekeep);self.assertTrue(seen.wait(2));attempt=threading.Event();self.scene.d.started.clear();self.scene.d.commit_block=threading.Event();self.releases.append(self.scene.d.commit_block)
  def ready():attempt.set();self.scene.event(record,'ready')
  commit,ce=self.launch(ready);self.assertTrue(attempt.wait(1));self.assertFalse(self.scene.d.started.wait(.04));permit.set();self.assertTrue(self.scene.d.started.wait(2));self.scene.d.commit_block.set();worker.join(3);commit.join(3);self.assertFalse(we);self.assertFalse(ce);self.assertEqual(len(record.results),3);self.assertTrue(all(r['outcome']=='complete'for r in self.closed(3)))
 def test_real_ingress_between_queries_with_explicit_cpu_source_line_gate(self):
  record=self.real_scene();between=threading.Event();resume=threading.Event();self.releases.append(resume);source=Path(__import__('native_runtime').__file__);lines=source.read_text().splitlines();number=next(i for i,s in enumerate(lines,1)if s.strip()=="native=query(['hyprctl','repl','print(hl.plugin.hyprbars.window_families())'])")
  def trace(frame,event,arg):
   if event=='line'and frame.f_code.co_filename==str(source)and frame.f_lineno==number:between.set();self.assertTrue(resume.wait(2))
   return trace
  def query():
   sys.settrace(trace)
   try:self.factory.housekeep()
   finally:sys.settrace(None)
  worker,we=self.launch(query);self.assertTrue(between.wait(2));self.assertEqual(self.data,EXPECTED[:1]);commit,ce=self.launch(lambda:self.scene.event(record,'ready'));commit.join(2);self.assertFalse(commit.is_alive());self.assertFalse(ce);self.assertEqual(len(record.results),3);resume.set();worker.join(3);self.assertFalse(we);self.assertEqual(self.data,EXPECTED);self.closed(3)
  EVIDENCE.append({'case':'actual-native-ready-between-observations','source':str(source),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'lineGate':number,'gatingIsExplicitCPUFixture':True,'cpuCommitResults':record.results})
 def test_slow_real_peer_keeps_original_point_six_deadline_and_closed_refusal(self):
  def slow(c,d):self.data.append(d.decode('ascii'));c.sendall(b'[');time.sleep(.67);c.sendall(b']')
  self.ipc.handler=slow
  with self.assertRaises(TimeoutError):self.factory.housekeep()
  row=self.closed(1)[0];self.assertEqual(row['outcome'],'refused');self.assertEqual(row['error']['type'],'TimeoutError');self.assertEqual(self.data,['j/clients']);self.assert_unlock()
 def test_partial_json_eof_remains_closed_durable_refusal(self):
  self.ipc.handler=lambda c,d:c.sendall(b'[{')
  with self.assertRaises(ValueError):self.factory.housekeep()
  row=self.closed(1)[0];self.assertEqual(row['outcome'],'refused');self.assertTrue(row['evidence']['completeServerEOF']);self.assert_unlock()
 def test_wrong_top_level_shape_remains_closed_refusal(self):
  self.ipc.handler=lambda c,d:c.sendall(b'{}')
  with self.assertRaises(ValueError):self.factory.housekeep()
  self.assertEqual(self.closed(1)[0]['outcome'],'refused');self.assert_unlock()
 def test_owner_replaced_after_peer_reply_remains_refusal(self):
  original=deepcopy(self.ipc.lease.owner)
  def replace(c,d):self.ipc.lease.owner['nonce']='e'*32;self.ipc.lease.publish_owner();c.sendall(b'[]')
  self.ipc.handler=replace
  try:
   with self.assertRaises(ValueError):self.factory.housekeep()
   self.assertEqual(self.closed(1)[0]['outcome'],'refused');self.assert_unlock()
  finally:self.ipc.lease.owner=original;self.ipc.lease.publish_owner()
 def test_socket_inode_replaced_after_reply_refuses(self):
  retained=self.ipc.socket.with_name('retained.sock')
  def replace(c,d):self.ipc.socket.rename(retained);self.ipc.socket.touch(mode=0o600);c.sendall(b'[]')
  self.ipc.handler=replace
  try:
   with self.assertRaises(ValueError):self.factory.housekeep()
   self.assertEqual(self.closed(1)[0]['outcome'],'refused');self.assert_unlock()
  finally:
   if retained.exists():self.ipc.socket.unlink();retained.rename(self.ipc.socket)
 def test_actual_completion_fsync_fault_latches_and_releases_admission(self):
  def failure(body):
   if any(r['outcome']=='complete'for r in body['history']):raise OSError('actual completion persistence fault')
  self.ipc.writer_fault=failure
  with self.assertRaisesRegex(OSError,'persistence'):self.factory.housekeep()
  self.assertTrue(self.ipc.reader.fault);self.assertEqual(self.ipc.store.read()['readonlyOwnership']['history'][-1]['outcome'],'pending');self.assert_unlock();self.ipc.writer_fault=None
  with self.assertRaisesRegex(ValueError,'revoked'):self.factory.housekeep()
 def test_later_healthy_queries_do_not_erase_original_closed_refusal(self):
  self.ipc.handler=lambda c,d:c.sendall(b'[{')
  with self.assertRaises(ValueError):self.factory.housekeep()
  old=self.closed(1)[0];self.ipc.handler=lambda c,d:(self.data.append(d.decode('ascii')),c.sendall(b'[]'));self.factory.housekeep();rows=self.closed(4);self.assertEqual(rows[0],old);self.assertTrue(all(r['outcome']=='complete'for r in rows[1:]));self.assertEqual(self.data,EXPECTED)
 def test_changed_complete_family_refuses_prune_between_real_queries(self):
  replies=iter([b'[]',b'[{"address":"0xaa","stableId":"aa","pid":41,"mapped":true}]',b'[]']);self.ipc.handler=lambda c,d:c.sendall(next(replies))
  with patch.object(self.factory.shared_cache,'prune',side_effect=AssertionError('coverage failure must not prune'))as prune:
   with self.assertRaisesRegex(ValueError,'coverage'):self.factory.housekeep()
   prune.assert_not_called()
  self.assertTrue(all(r['outcome']=='complete'for r in self.closed(3,[2,59,2])));self.assert_unlock()
 def test_actual_housekeeping_error_loop_never_clears_prior_failure(self):
  self.ipc.handler=lambda c,d:c.sendall(b'[{');error_root=self.ipc.root/'errors';error_root.mkdir(mode=0o700);store=JournalStore(error_root,self.ipc.session);service=RuntimeService.__new__(RuntimeService);service.stop_requested=threading.Event();service.housekeeping_errors=[];rounds=[]
  def reap():
   rounds.append(1);self.ipc.handler=lambda c,d:c.sendall(b'[]')
   if len(rounds)==2:service.stop_requested.set()
  service.manager=types.SimpleNamespace(factory=self.factory,reap_idle=reap,lock=self.ipc.lock,persistence_failed=False)
  def persist():store.write({'version':1,'session':self.ipc.session,'snapshot':1,'scenes':[],'pending':[],'housekeepingErrors':deepcopy(service.housekeeping_errors)})
  service.persist=persist;worker,we=self.launch(service.housekeep);worker.join(5);self.assertFalse(worker.is_alive());self.assertFalse(we);self.assertEqual(len(service.housekeeping_errors),1);self.assertEqual(service.housekeeping_errors[0]['operation'],'cache');self.assertEqual(store.read()['housekeepingErrors'],service.housekeeping_errors);rows=self.closed(4);self.assertEqual(rows[0]['outcome'],'refused');self.assertTrue(all(r['outcome']=='complete'for r in rows[1:]));self.assert_unlock()
  EVIDENCE.append({'case':'actual-RuntimeService-housekeeping-error-latch','housekeepingErrors':deepcopy(service.housekeeping_errors),'journal':store.read(),'fixturePersistWritesOwnedJournalStore':True})
 def test_missing_shared_lock_never_falls_back_to_unprotected_query(self):
  self.factory.journal_lock=None
  with self.assertRaises(TypeError):self.factory.housekeep()
  self.assertEqual(self.ipc.reader.rows,{});self.assertEqual(self.data,[])
