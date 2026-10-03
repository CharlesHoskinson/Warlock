"""Owned actual PipeTransport and CPU producer; no GUI/native artifact."""
from pathlib import Path
import hashlib,json,os,sys,threading,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
S=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-reduced-validation-v18');sys.path.insert(0,str(S))
from test_pipe_transport import TransportTests
scope=require_qa_scope();f=TransportTests();f.setUp();entered=threading.Event();release=threading.Event()
def failure(reason):
 entered.set();release.wait(2);f.failures.append(reason)
f.t.failure=failure
try:
 f.wait(lambda:f.t.outputs());start=time.monotonic();f.t.send({'command':'malformed'});assert entered.wait(1)
 cue=dict(failed=f.t.failed,actualReceiptCount=len(f.failures),elapsedSeconds=time.monotonic()-start)
 assert cue['failed']and cue['actualReceiptCount']==0
 release.set();deadline=start+2
 while time.monotonic()<deadline and not(f.t.failed and f.failures):time.sleep(.002)
 assert f.t.failed and len(f.failures)==1
 try:f.t.send({'command':'state'})
 except BrokenPipeError:sendRefused=True
 else:raise AssertionError('failed transport accepted send')
 try:f.t.close()
 except RuntimeError as error:normalCloseRefused=str(error)
 else:raise AssertionError('failed transport accepted normal close')
 f.t.failure_thread.join(timeout=max(0,deadline-time.monotonic()));assert not f.t.failure_thread.is_alive()
 row=dict(result='actual failed cue precedes genuine callback receipt',scope=scope,cue=cue,receiptCount=len(f.failures),sendRefused=sendRefused,normalCloseRefused=normalCloseRefused,producerPID=f.t.process.pid,producerActualExit=f.t.process.returncode,failureThreadGone=True,elapsedSeconds=time.monotonic()-start,originalDeadlineSeconds=2,sourceSHA256={n:hashlib.sha256((S/n).read_bytes()).hexdigest()for n in ('pipe_transport.py','test_pipe_transport.py')},nativeLaunch=False,productChanged=False)
finally:release.set();f.tearDown()
fd=os.open(Path(__file__).with_name('result.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps(row))
