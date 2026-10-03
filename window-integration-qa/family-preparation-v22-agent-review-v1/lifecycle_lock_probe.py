"""Actual frozen stage and unrelated cleanup with a gated actual file read."""
from pathlib import Path
import hashlib,json,os,sys,threading,time
from unittest.mock import patch
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v22');sys.path.insert(0,str(B))
from test_batch_preview import BatchTests,patterned_png
from native_desktop import NativeDesktop
import batch_preview
scope=require_qa_scope();f=BatchTests();f.setUp();entered=threading.Event();release=threading.Event();cleanupEntered=threading.Event();cleaned=threading.Event();reserved=threading.Event();errors=[]
receipt=threading.RLock();actor=NativeDesktop.__new__(NativeDesktop);actor.root=f.actor;actor.preview_batch=f.batch;actor.janitor=lambda:None
old=f.actor/'abcdef123456-99.png';old.write_bytes(patterned_png(2,2));old.chmod(0o600)
original=os.pread;once=[False]
def gated(fd,size,offset):
 if threading.current_thread().name=='stage-material-reader'and not once[0]:
  once[0]=True;entered.set()
  if not release.wait(2):raise TimeoutError('owned material probe read gate')
 return original(fd,size,offset)
def stage():
 try:f.stage([(20,20,2,2,True,1)])
 except BaseException as error:errors.append(repr(error))
def cleanup():
 try:
  with receipt:cleanupEntered.set();actor.release_sources([{'path':str(old)}]);cleaned.set()
 except BaseException as error:errors.append(repr(error))
def reserve():
 with receipt:reserved.set()
worker=threading.Thread(target=stage,name='stage-material-reader');cleanupThread=threading.Thread(target=cleanup);request=threading.Thread(target=reserve)
try:
 with patch.object(batch_preview.os,'pread',gated):
  worker.start();assert entered.wait(1);cleanupThread.start();assert cleanupEntered.wait(1);request.start();start=time.monotonic();reservedBeforeRelease=reserved.wait(.15);cleanedBeforeRelease=cleaned.is_set();elapsed=time.monotonic()-start
  release.set();worker.join(2);cleanupThread.join(2);request.join(2)
 assert not any(t.is_alive()for t in (worker,cleanupThread,request))and not errors
 row=dict(result='lifecycle material read blocks unrelated receipt cleanup'if not reservedBeforeRelease and not cleanedBeforeRelease else 'counterexample not reproduced',scope=scope,sourceSHA256={n:hashlib.sha256((B/n).read_bytes()).hexdigest()for n in ('batch_preview.py','native_desktop.py')},observation=dict(actualOwnedPNGReadEntered=True,actualStageHeldLifecycleLock=True,actualCleanupEnteredSharedReceipt=True,unrelatedOldEpoch='abcdef123456-99',cleanupReturnedBeforeReadRelease=cleanedBeforeRelease,receiptAcquiredBeforeReadRelease=reservedBeforeRelease,observationSeconds=elapsed,cleanupReturnedAfterReadRelease=cleaned.is_set(),receiptAcquiredAfterReadRelease=reserved.is_set(),oldSourceGone=not old.exists(),allThreadsTerminal=True),nativeLaunch=False,productChanged=False,scopeLimit='actual frozen BatchPreviews.stage and NativeDesktop.release_sources; shared receipt lock as actual cleanup caller; CPU gated material read, no claim of measured native stall')
finally:
 release.set()
 for t in (worker,cleanupThread,request):
  if t.ident:t.join(2)
 f.tearDown()
fd=os.open(Path(__file__).with_name('lifecycle-lock-counterexample.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps(row));raise SystemExit(row['result']=='counterexample not reproduced')
