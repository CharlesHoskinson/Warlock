"""Deterministic CPU-only V17 lock counterexample; never starts native work."""
from pathlib import Path
from types import SimpleNamespace
import json,os,sys,threading,time,traceback,hashlib
BASE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-recovery-terminal-v17')
sys.path.insert(0,str(BASE))
from scene_manager import SceneManager,ManagedController
from scene_controller import Scene,ids,key
from native_desktop import NativeDesktop
from helper_supervisor import Keeper
from direction import Direction
familyHeld=threading.Event();watchdogHeld=threading.Event();manager=SceneManager(lambda _:None)
keeper=Keeper.__new__(Keeper);keeper.reservation_lock=manager.lock;keeper.lock=threading.RLock()
window={'address':'0xaa01','stableId':'aa01','pid':41,'at':[100,100],'size':[300,200],'mapped':True}
desktop=NativeDesktop.__new__(NativeDesktop);desktop.family_query_lock=threading.RLock();desktop.family_query_local=threading.local();desktop.base=SimpleNamespace(family_trace=threading.local())
desktop.clients=lambda:[dict(window)];desktop.reduced=lambda:False;desktop.commit=lambda *a:(_ for _ in ()).throw(AssertionError('CPU fixture must never commit'));desktop.release_sources=lambda _:None
# The actual NativeDesktop.family lock encloses the actual Keeper.register
# reservation lock, just as its ordinary production family helper does.
def family(window,windows,single):
 familyHeld.set();assert watchdogHeld.wait(1)
 keeper.register({},kind='helper',actor=1)
 raise AssertionError('actual helper lock should still be blocked')
desktop._family_locked=family
class Transport:
 def set_callback(self,cb):self.callback=cb
 def send(self,m):raise AssertionError('cleanup cannot be reached during this deadlock')
controller=ManagedController(manager,desktop,Transport());record=Scene('abcdefabcdef-1','minimize',key(window),{},members=[window],focus=key(window),validated=True,visual=True,running=True,ready=True,accepted_operation='minimize',direction=Direction('minimize'),profile={'managerReceipt':1,'receivedNs':time.monotonic_ns()-3000000000})
controller.current=record;manager.receipts[key(window)]=1;manager.owners[key(window)]=controller
errors=[]
def endpoint():
 try:controller.event({'event':'endpoint','token':record.token,'identities':ids(record.members),'servicePromoted':True,'sourceDigests':[]})
 except BaseException:errors.append(traceback.format_exc())
def watchdog():
 # This is the exact shared lock already held by SceneController.watchdog.
 # External acquire only makes its existing acquire order deterministic.
 with manager.lock:
  watchdogHeld.set();controller.watchdog()
a=threading.Thread(target=endpoint,name='actual-endpoint',daemon=True);a.start();assert familyHeld.wait(1)
b=threading.Thread(target=watchdog,name='actual-watchdog',daemon=True);b.start();assert watchdogHeld.wait(1)
time.sleep(.05)
frames=sys._current_frames();stacks={t.name:''.join(traceback.format_stack(frames[t.ident])) for t in (a,b)}
assert a.is_alive() and b.is_alive() and not errors
assert 'self.reservation_lock,self.lock' in stacks[a.name]
assert 'family_query_lock' in stacks[b.name]
assert 'self.settle' in stacks[b.name]
result={'result':'counterexample-confirmed','nativeLaunch':False,'nativeWrites':0,'exactFrozenSource':{n:hashlib.sha256((BASE/n).read_bytes()).hexdigest() for n in ('scene_controller.py','scene_manager.py','native_desktop.py','helper_supervisor.py')},'bothThreadsBlocked':True,'currentSceneRetained':controller.current is record,'cleanupQueued': 'cleanupQueuedNs' in record.profile,'stacks':stacks,'scope':'CPU source interleaving reproduces exact two production lock sites; no surviving private native thread stack was archived'}
print(json.dumps(result,indent=2),flush=True)
os._exit(0)
