from pathlib import Path
import sys,threading,time,json,hashlib,os,copy
B=Path(__file__).resolve().parent
S=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-responsive-v13')
sys.path.insert(0,str(S))
from scene_manager import SceneManager
from test_scene_controller import Desktop,Transport
from scene_controller import key
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=Desktop();t=Transport();d.block=threading.Event()
m=SceneManager(lambda number:(d,t));before=copy.deepcopy(d.windows);rows=[]
try:
 w=d.windows[0];reply=m.request('minimize',w['address'],w['stableId'],w['pid'],context='trusted-fixture')
 assert d.started.wait(1),'Actual worker did not enter blocked family lookup'
 c=m.actors[0].controller;record=c.current
 assert record and not record.validated and not record.profile['contextPending']
 rows.append({'phase':'accepted-and-validation-blocked','reply':reply,'token':record.token,'validated':record.validated,'contextPending':record.profile['contextPending'],'commits':copy.deepcopy(d.commits)})
 d.reduced_flag=True;m.watchdog()
 rows.append({'phase':'reduction-watchdog','currentNone':c.current is None,'historyTokens':[r.token for r in c.history],'commits':copy.deepcopy(d.commits),'sent':copy.deepcopy(t.sent),'profile':dict(record.profile)})
 d.block.set();c.workers.shutdown(wait=True,cancel_futures=False)
 rows.append({'phase':'validation-worker-finished','currentNone':c.current is None,'commits':copy.deepcopy(d.commits),'sent':copy.deepcopy(t.sent),'nativeFixtureWindows':copy.deepcopy(d.windows),'ingressHistory':copy.deepcopy(m.ingress_history)})
 proof={'scope':'Unmodified staged SceneManager/ManagedController/SceneController with inherited deterministic Desktop/Transport CPU fixtures; no compositor/native/real user command execution','sourceHashes':{n:sha(S/n) for n in ['scene_manager.py','scene_controller.py','test_scene_controller.py','direction.py']},'observations':rows,'acceptedReceipt':reply['accepted'],'validationBeforeReduction':record.validated,'requestRetiredBeforeValidation':rows[1]['currentNone'],'lateWorkerCannotComplete':not d.commits and c.current is None,'fixtureNativeStateUnchanged':d.windows==before,'actualNativeWrites':False,'actualGuiModified':False,'counterexampleEstablished':reply['accepted'] and rows[1]['currentNone'] and not d.commits and d.windows==before,'physicalReducedMotionAccepted':False}
 p=B/'result.json'
 with p.open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
 p.chmod(0o600);print(json.dumps({k:proof[k] for k in ['acceptedReceipt','requestRetiredBeforeValidation','lateWorkerCannotComplete','fixtureNativeStateUnchanged','counterexampleEstablished','actualNativeWrites']}))
finally:
 d.block.set()
 for a in m.actors:a.controller.workers.shutdown(wait=True,cancel_futures=True)
