"""Bounded CPU counterexample for a current-tip borrow before row/slot reservation."""
from pathlib import Path
import hashlib,json,os,threading,time
import readonly_ipc
import test_readonly_ipc as fixture

f=fixture.ReadonlyKernelTests();f.setUp();old_capacity=readonly_ipc.MAX_HISTORY
readonly_ipc.MAX_HISTORY=2
release=threading.Event();waiting=[threading.Event() for _ in range(4)];threads=[];errors=[]
original=f.reader.ensure_capacity
sources={str(Path(n).resolve()):hashlib.sha256(Path(n).read_bytes()).hexdigest() for n in ['readonly_ipc.py','readonly_current.py']}
def ensure(remaining):
 name=threading.current_thread().name
 if name.startswith('pre-register-'):
  waiting[int(name.rsplit('-',1)[1])].set();release.wait(remaining())
 return original(remaining)
def query():
 try:f.query()
 except BaseException as e:errors.append({'type':type(e).__name__,'message':str(e)})
f.reader.ensure_capacity=ensure
try:
 for i in range(4):
  f.query()
  t=threading.Thread(target=query,name=f'pre-register-{i}');threads.append(t);t.start()
  assert waiting[i].wait(.3)
  deadline=time.monotonic()+1
  f.reader.rotate_closed(lambda:deadline-time.monotonic())
 raw={'version':1,'runtimeSHA256':sources,'capacity':2,'blockedActualQueries':4,'registeredRows':len(f.reader.rows),
      'registeredReferences':len(f.reader.references),'heldTips':len(f.reader.current.tips),
      'heldReferences':sum(t.references for t in f.reader.current.tips),'ownedDataFDs':3+sum((2 if t.fd is not None else 1) for t in f.reader.current.tips),
      'modelBoundIncludingPreparingPair':2*(2+2)+3,'nativeLaunch':False,'deadlineUnchanged':True}
 Path('unregistered-tip-slot-counterexample.json').write_text(json.dumps(raw,indent=2)+'\n')
 assert raw['heldTips']>2+2 and raw['ownedDataFDs']>raw['modelBoundIncludingPreparingPair']
 print(json.dumps(raw),flush=True)
finally:
 release.set()
 for t in threads:t.join(2)
 readonly_ipc.MAX_HISTORY=old_capacity;f.reader.current.close(force=True);f.tearDown()
