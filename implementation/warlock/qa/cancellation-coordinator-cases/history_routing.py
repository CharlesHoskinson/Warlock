from coordinator_fixture import *
import importlib.util
spec=importlib.util.spec_from_file_location('routing_candidate_daemon',ROOT/'adapter/daemon.py');daemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(daemon)

class NewNative(Native):
 def request(self,payload):
  result=super().request(payload)
  if payload['kind']=='hello':result['binding']={**BOUND,'frontend':'4'}
  return result

for phase in ['prepared','acknowledged','certificate-before-finish']:
 with fixture() as (store,native,coordinator,events,depth,hello):
  prepared=prepare(store,coordinator)
  if phase=='acknowledged':coordinator.handle(request('effect-cancel',prepared))
  if phase=='certificate-before-finish':
   with patch.object(store,'cancellation_finish',side_effect=OSError('interrupted after certificate store')):
    refused(lambda:coordinator.handle(request('effect-cancel',prepared)),'interrupted finish refuses terminal publication')
  before=store.cancellation_snapshot(BOUND)[0];runtime=store.path.parents[2]
  old_calls=copy.deepcopy(native.calls);coordinator.close();store.close()
  with RecoveryStore(runtime,'coordinatorqa','1',cancellation=True) as reopened:
   Navigation(reopened);next_events=[];new_client=NewNative(next_events,[0]);new_hello=new_client.hello();new=CancellationCoordinator(new_client,reopened,new_hello,settlement_sink=lambda frame:None)
   try:
    frames=new.startup();history=[f for f in frames if f['kind']=='host-cancellation-recovery'];settled=[f for f in frames if f['kind']=='host-cancellation-settled']
    check(len(history)==1,'nonempty startup emits exactly one historical recovery record '+phase)
    check(len(settled)==(0 if phase=='prepared' else 1),'typed local settlement exists only for stored terminal '+phase)
    if settled:check(settled[0]['binding']==new_client.bound and settled[0]['admission']['binding']==BOUND and settled[0]['certificate']==before['certificate']['response'] and settled[0]['executionAuthorized'] is False,'new historical cleanup preserves exact old native certificate '+phase)
    frame=history[0]
    check(frame['binding']==new_client.bound and frame['record']['admission']['binding']==BOUND and frame['executionAuthorized'] is False,'historical frame separates new delivery binding and immutable old owner '+phase)
    check(frame['recoveryState']==('Unknown' if phase=='prepared' else 'Terminal'),'historical state reflects actual certification '+phase)
    for field in ['admission','deadlineMonotonicNs','prepared','certificate','attemptedKinds','commitAttempted']:
     check(frame['record'][field]==before[field],'historical original '+field+' retained '+phase)
    check(count(new_client,'effect-decision-request')==0 and count(new_client,'effect-decision-ack')==0 and count(new_client,'effect-commit')==0,'startup never queries/ACKs/replays old grant '+phase)
    check(native.calls==old_calls,'restart does not reuse previous client '+phase)
    new.handle({**request('effect-cancellation-negotiate'),'binding':copy.deepcopy(new_client.bound)})
    forged=request('effect-commit',prepared);forged['binding']=copy.deepcopy(new_client.bound);forged['intent']['context']['epoch']='4'
    refused(lambda:new.handle(forged),'historical preparation is not new-grant effect authority '+phase)
    check(count(new_client,'effect-commit')==0,'old handle cannot authorize native commit '+phase)
   finally:new.close()

with fixture() as (store,native,coordinator,events,depth,hello):
 frames=[]
 with patch.object(daemon,'send',frames.append):
  before=copy.deepcopy(native.calls)
  refused(lambda:daemon.handle_request(native,None,request('effect-prepare'),store,None),'default request handler refuses new lifecycle kinds')
  check(native.calls==before and frames==[],'default unsupported lifecycle has no fallback/native effect')
  daemon.handle_request(native,None,request('effect-cancellation-negotiate'),store,None,cancellation=coordinator)
  check(frames[-1]['kind']=='effect-cancellation-capabilities','explicit coordinator handler routes strict negotiated capability')
  cancellation_pending(store,intent())
  daemon.handle_request(native,None,request('effect-prepare'),store,None,cancellation=coordinator)
  prepared=frames[-1];check(prepared['kind']=='effect-prepared','explicit coordinator handler routes exact prepared reply')
  daemon.handle_request(native,None,request('effect-commit',prepared),store,None,cancellation=coordinator)
  check(frames[-1]['status']=='Committed' and count(native,'effect-commit')==1 and count(native,'effect-decision-ack')==1,'explicit handler reaches one durably settled commit and ACK')
print(json.dumps({'passed':True,'checks':len(checks),'nativeAcceptance':False,'scope':'Actual coordinator startup and candidate daemon dispatch with real V7 across reopened grants; strict response doubles, no real C/Elm/transport/window proof.'}))
