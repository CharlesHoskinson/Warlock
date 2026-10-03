"""CPU/kernel lock regressions; no compositor, renderer or GUI process."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import hashlib,json,os,subprocess,sys,tempfile,threading,time,unittest
from scene_manager import SceneManager,ManagedController
from scene_controller import Scene,key,ids
from native_desktop import NativeDesktop
from helper_supervisor import Keeper
from owned_commands import OwnedCommands
from direction import Direction

class Transport:
 def __init__(self):self.sent=[]
 def set_callback(self,cb):self.callback=cb
 def send(self,value):self.sent.append(deepcopy(value))

class QueryConcurrency(unittest.TestCase):
 def test_actual_keeper_cpu_jobs_allow_watchdog_and_endpoint_to_finish(self):
  # Actual Keeper/OwnedCommands register sealed confined CPU cat groups. The
  # unmodified controller methods exercise the retained deadline interleaving.
  with tempfile.TemporaryDirectory() as d:
   env=dict(os.environ,XDG_RUNTIME_DIR=d,HYPRLAND_INSTANCE_SIGNATURE='cpu-only',WAYLAND_DISPLAY='never-connect')
   m=SceneManager(lambda _:None);snapshots=[];keeper=Keeper(Path(d),env,lambda r:snapshots.append(deepcopy(r)),reservation_lock=m.lock)
   family_entered=threading.Event();watchdog_entered=threading.Event();errors=[];commits=[];t=Transport()
   w={'address':'0xaa01','stableId':'aa01','pid':41,'at':[100,100],'size':[300,200],'mapped':True}
   n=NativeDesktop.__new__(NativeDesktop);n.family_query_local=threading.local();n.base=SimpleNamespace(family_trace=threading.local());n.clients=lambda:[deepcopy(w)];n.reduced=lambda:False;n.commit=lambda *args:commits.append(args);n.release_sources=lambda _:None
   commands=OwnedCommands(keeper,env,1)
   def family(window,windows,single):
    if threading.current_thread().name=='endpoint':
     family_entered.set()
     if not watchdog_entered.wait(2):raise TimeoutError('watchdog did not own manager lock')
    result=commands.run(['/usr/bin/cat'],input='actual CPU query\n',capture_output=True,text=True,timeout=2,check=True)
    if result.stdout!='actual CPU query\n':raise AssertionError('real CPU query output differs')
    n.base.family_trace.evidence={'worker':threading.current_thread().name}
    return [deepcopy(w)],deepcopy(w)
   n._family_locked=family;c=ManagedController(m,n,t);r=Scene('abcdefabcdef-1','minimize',key(w),{},members=[w],focus=key(w),validated=True,visual=True,running=True,ready=True,accepted_operation='minimize',direction=Direction('minimize'),profile={'managerReceipt':1,'receivedNs':time.monotonic_ns()-3000000000});c.current=r;m.receipts[key(w)]=1;m.owners[key(w)]=c
   def endpoint():
    try:c.event({'event':'endpoint','token':r.token,'identities':ids(r.members),'servicePromoted':True,'sourceDigests':[]})
    except BaseException as e:errors.append(e)
   def watchdog():
    try:
     with m.lock:watchdog_entered.set();c.watchdog()
    except BaseException as e:errors.append(e)
   a=threading.Thread(target=endpoint,name='endpoint',daemon=True);b=threading.Thread(target=watchdog,name='watchdog',daemon=True)
   try:
    a.start();self.assertTrue(family_entered.wait(2));b.start();a.join(5);b.join(5)
    self.assertFalse(a.is_alive());self.assertFalse(b.is_alive());self.assertEqual(errors,[])
    self.assertIn('cleanupQueuedNs',r.profile);self.assertEqual(r.profile['settlementReason'],'native handover complete')
    self.assertEqual(len(commits),1);self.assertTrue(any(row['jobs'] for row in snapshots));self.assertEqual(keeper.jobs,{})
    keeper.stop();terminal=keeper.read_terminal();self.assertEqual(terminal['registrations'],2);self.assertTrue(terminal['normalStop']);self.assertTrue(all(x['normalCompletion'] and x['groupEmpty'] for x in terminal['jobs']))
   finally:
    c.workers.shutdown(wait=True,cancel_futures=True)
    if not keeper.closed:keeper.detach();keeper.process.wait(timeout=5);keeper.process.stderr.close()
 def test_actual_family_body_keeps_simultaneous_evidence_in_each_thread(self):
  n=NativeDesktop.__new__(NativeDesktop);n.family_query_local=threading.local();barrier=threading.Barrier(2);n.base=SimpleNamespace(family_trace=threading.local())
  def base_family(w,ws,single):
   n.base.family_trace.evidence={'worker':w['stableId']};barrier.wait(2);return [deepcopy(w)],deepcopy(w)
  n.base.family=base_family;results={};errors=[]
  def query(sid):
   try:
    w={'address':'0x'+sid,'stableId':sid,'pid':41};n.family(w,[w],True);results[sid]=n.family_evidence()
   except BaseException as e:errors.append(e)
  a=threading.Thread(target=query,args=('aa01',),daemon=True);b=threading.Thread(target=query,args=('bb02',),daemon=True);a.start();b.start();a.join(3);b.join(3)
  self.assertFalse(a.is_alive());self.assertFalse(b.is_alive());self.assertEqual(errors,[])
  self.assertEqual(results['aa01']['drawOrder'],[['0xaa01','aa01',41]]);self.assertEqual(results['bb02']['drawOrder'],[['0xbb02','bb02',41]])
 def test_actual_delayed_failure_callback_cannot_complete_from_failed_flag_alone(self):
  from pipe_transport import PipeTransport
  from test_pipe_transport import SCRIPT,TransportTests
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'cpu-pipe';path.write_text(SCRIPT);path.chmod(0o700)
   entered=threading.Event();release=threading.Event();receipts=[]
   def failure(reason):entered.set();release.wait(1);receipts.append(reason)
   t=PipeTransport(path,env=dict(os.environ),failure=failure);timer=None
   try:
    t.send({'command':'malformed'});self.assertTrue(entered.wait(1))
    self.assertTrue(t.failed);self.assertEqual(receipts,[])
    self.assertFalse(bool(t.failed and receipts))
    timer=threading.Timer(.03,release.set);timer.start()
    # Exact inherited single 2s wait and its receipt predicate, no new deadline.
    TransportTests.wait(self,lambda:t.failed and receipts)
    self.assertEqual(len(receipts),1)
    with self.assertRaises(BrokenPipeError):t.send({'command':'state'})
    with self.assertRaises(RuntimeError):t.close()
    self.assertIsNotNone(t.process.returncode);t.failure_thread.join(1);self.assertFalse(t.failure_thread.is_alive())
   finally:
    release.set()
    if timer:timer.join(1)
    try:t.close()
    except RuntimeError:pass
 def test_actual_delayed_retirement_callback_cannot_bless_unpublished_completion(self):
  from service_runtime import RuntimeService,JournalStore
  from test_actor_resources import Factory
  entered=threading.Event();release=threading.Event()
  class DelayedFactory(Factory):
   def retired(self,number,desktop):
    super().retired(number,desktop);entered.set()
    if not release.wait(2):raise TimeoutError('delayed fixture retirement refused')
  with tempfile.TemporaryDirectory(prefix='v19-') as d:
   root=Path(d)/'runtime';root.mkdir(mode=0o700);factory=DelayedFactory()
   service=RuntimeService(root,'fixture',factory,lambda _:'context')
   try:
    w=factory.desktop.windows[0];r=service.manager.reserve('minimize',w['address'],w['stableId'],w['pid']);service.manager.fail_ingress(r['receipt'],'fixture refusal');service.start()
    self.assertTrue(entered.wait(2));self.assertEqual(factory.retired_ids,[1])
    body=JournalStore(root,'fixture').read();self.assertEqual(body['retiringActors'],[1]);self.assertFalse(body['liveActors'])
    def complete():return factory.retired_ids==[1] and not JournalStore(root,'fixture').read()['retiringActors']
    self.assertFalse(complete());release.set();deadline=time.monotonic()+3
    while time.monotonic()<deadline and not complete():time.sleep(.01)
    self.assertTrue(complete());self.assertEqual(factory.retired_ids,[1]);self.assertEqual(service.manager.retiring,[]);self.assertFalse(service.manager.resource_errors)
   finally:release.set();service.close()
 def test_retained_old_source_counterexample_still_blocks_exact_two_sites(self):
  path=Path('/home/hoskinson/window-integration-qa/recovery-baseline-v2-lock-counterexample-v1/replay.py');r=subprocess.run([sys.executable,str(path)],capture_output=True,text=True,timeout=3,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'));self.assertEqual(r.returncode,0,r.stderr);result=json.loads(r.stdout);self.assertTrue(result['bothThreadsBlocked']);self.assertFalse(result['cleanupQueued']);self.assertEqual(result['nativeWrites'],0)
if __name__=='__main__':unittest.main()
