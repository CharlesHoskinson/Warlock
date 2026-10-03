"""Exact current V18 frontend/controller with fake Desktop; no GUI."""
from pathlib import Path
import hashlib,json,os,sys,threading,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
S=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-reduced-validation-v18');sys.path.insert(0,str(S))
from test_socket_frontend import FrontendTests
scope=require_qa_scope();f=FrontendTests();f.setUp()
try:
 f.d.block=threading.Event();first=f.request();assert f.entered.wait(1);second=f.request(op='restore');start=time.monotonic();f.gate.set();f.wait(lambda:not f.m.pending)
 active=[a.controller.current for a in f.m.actors if a.controller.current];cue=dict(pendingEmpty=not f.m.pending,activeSceneCount=len(active),sceneReceipt=active[0].profile['managerReceipt']if active else None,validated=active[0].validated if active else None,commits=list(f.d.commits),elapsedSeconds=time.monotonic()-start)
 assert cue['pendingEmpty']and cue['activeSceneCount']==1 and cue['sceneReceipt']==second['receipt']and not cue['validated']and not cue['commits']
 f.d.block.set();deadline=start+2
 while time.monotonic()<deadline and any(a.controller.current for a in f.m.actors):time.sleep(.002)
 assert not any(a.controller.current for a in f.m.actors);done=f.m.actors[0].controller.history[-1]
 assert len(f.d.commits)==3 and done.profile['managerReceipt']==second['receipt']and done.operation=='restore'and done.profile['nativeEndpointAlreadySatisfied']and not any(t.sent for t in f.transports)
 row=dict(result='actual cue precedes completion; original strict outcome later completes',scope=scope,sourceSHA256={n:hashlib.sha256((S/n).read_bytes()).hexdigest()for n in ('test_socket_frontend.py','socket_frontend.py','scene_controller.py','scene_manager.py')},cue=cue,originalLatestReceipt=second['receipt'],finalReceipt=done.profile['managerReceipt'],originalOperation=done.operation,nativeEndpointAlreadySatisfied=done.profile['nativeEndpointAlreadySatisfied'],actualFakeEffects=f.d.commits,elapsedSeconds=time.monotonic()-start,originalDeadlineSeconds=2,allOriginalOutcomeAssertionsPreserved=True,nativeLaunch=False,productChanged=False)
finally:
 f.d.block.set();f.tearDown()
fd=os.open(Path(__file__).with_name('result.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps(row))
