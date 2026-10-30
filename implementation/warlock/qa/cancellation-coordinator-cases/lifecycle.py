from coordinator_fixture import *
for terminal_kind,status in [('effect-cancel','Cancelled'),('effect-commit','Committed')]:
 with fixture() as (store,native,coordinator,events,depth,hello):
  check(coordinator.startup()==[],'empty startup is informational and emits no effect')
  prepared=prepare(store,coordinator)
  check(count(native,'effect-prepare')==1,'one first native prepare')
  check(coordinator.handle(request('effect-prepare'))==prepared and count(native,'effect-prepare')==1,'duplicate prepare returns stored response without replay')
  events.clear();admission_name=storage_key(admission(intent()))+'.json';real_unlink=os.unlink;real_sync=os.fsync;inode=(store.path/'admissions-v1').stat().st_ino
  def unlink(name,**kwargs):
   result=real_unlink(name,**kwargs)
   if name==admission_name:events.append('admission-unlinked')
   return result
  def sync(fd):
   result=real_sync(fd)
   if stat.S_ISDIR(os.fstat(fd).st_mode) and os.fstat(fd).st_ino==inode:events.append('admissions-synced')
   return result
  with patch('os.unlink',unlink),patch('os.fsync',sync):outcome=coordinator.handle(request(terminal_kind,prepared))
  check(outcome['status']==status,'actual coordinator known terminal '+status)
  operation='commit' if terminal_kind=='effect-commit' else 'cancel'
  attempt=next(i for i,e in enumerate(events) if e=='stored:Uncertain:NotSent:prepare,'+operation)
  effect=events.index('rpc:'+terminal_kind);cert=next(i for i,e in enumerate(events) if e.startswith('stored:TerminalStored:'))
  unlink_index=events.index('admission-unlinked');dir_index=next(i for i,e in enumerate(events) if e=='admissions-synced' and i>unlink_index)
  retired=next(i for i,e in enumerate(events) if e.startswith('stored:AdmissionRetired:NotSent'))
  ack_pending=next(i for i,e in enumerate(events) if e.startswith('stored:AdmissionRetired:Pending'))
  ack=events.index('rpc:effect-decision-ack');acknowledged=next(i for i,e in enumerate(events) if e.startswith('stored:AdmissionRetired:Acknowledged'))
  check(attempt<effect<cert<unlink_index<dir_index<retired<ack_pending<ack<acknowledged,'durable/native/certificate/retirement/ACK order '+status)
  before=copy.deepcopy(native.calls)
  for kind in ['effect-commit','effect-cancel','effect-decision-request']:
   check(coordinator.handle(request(kind,prepared))==outcome,'late control returns exact stored terminal '+kind)
  check(coordinator.handle(request('effect-decision-ack',prepared))['kind']=='effect-decision-acknowledged','duplicate frontend ACK returns known exact ACK')
  check(native.calls==before,'late opposing controls and ACK perform zero new native RPC')

with fixture() as (store,native,coordinator,events,depth,hello):
 prepared=prepare(store,coordinator);native.reply_mode='unknown';unknown=coordinator.handle(request('effect-commit',prepared))
 check(unknown['status']=='Unknown' and count(native,'effect-commit')==1 and count(native,'effect-decision-ack')==0,'Unknown remains unACKed after one commit')
 native.reply_mode='prepared-after-unknown';queried=coordinator.handle(request('effect-decision-request',prepared))
 check(queried['kind']=='effect-prepared','adversarial correlated Prepared query reaches real store')
 before=count(native,'effect-commit');again=coordinator.handle(request('effect-commit',prepared))
 check(again==queried and count(native,'effect-commit')==before,'fresh Prepared cannot renew consumed commit permission')
 check(store.cancellation_snapshot(BOUND)[0]['commitAttempted'] is True,'real store retains consumed commit after query')

for case in ['reserve-fault','attempt-fault','binding-before','binding-after','double-attach','close']:
 with fixture() as (store,native,coordinator,events,depth,hello):
  if case=='double-attach':
   refused(lambda:CancellationCoordinator(native,store,hello,settlement_sink=lambda frame:None),'second coordinator cannot detach an existing live grant')
   check(coordinator.handle(request('effect-cancellation-negotiate'))['kind']=='effect-cancellation-capabilities','original grant survives second attach refusal');continue
  if case=='binding-before':
   native.bound={**BOUND,'frontend':'4'};before=copy.deepcopy(native.calls)
   refused(lambda:coordinator.handle(request('effect-cancellation-negotiate')),'binding drift before call refuses')
   check(coordinator.closed and native.calls==before,'binding drift detaches without RPC');continue
  if case=='close':
   coordinator.close();coordinator.close();before=copy.deepcopy(native.calls)
   refused(lambda:coordinator.handle(request('effect-cancellation-negotiate')),'closed coordinator refuses')
   check(native.calls==before and store.ledger._live_cancellation_binding is None,'idempotent close detaches before store close');continue
  if case in ['reserve-fault','attempt-fault']:
   coordinator.handle(request('effect-cancellation-negotiate'));pending(store,intent());original=store.ledger._write_file_locked
   def fail_write(name,body,limit):
    state=json.loads(body)
    if name=='ledger-v7.json' and state['cancellations']:
     row=state['cancellations'][-1]
     if (case=='reserve-fault' and row['stage']=='Reserved') or (case=='attempt-fault' and row['attemptedKinds']==['prepare']):store.ledger.poisoned=True;raise OSError('injected before durable permission')
    return original(name,body,limit)
   with patch.object(store.ledger,'_write_file_locked',fail_write):refused(lambda:coordinator.handle(request('effect-prepare')),'failed store permission refuses '+case)
   check(count(native,'effect-prepare')==0,'no prepare after failed durable store '+case)
   refused(lambda:coordinator.handle(request('effect-prepare')),'poisoned coordinator cannot continue '+case);continue
  prepared=prepare(store,coordinator);native.reply_mode='binding-drift'
  refused(lambda:coordinator.handle(request('effect-commit',prepared)),'binding drift during RPC refuses returned evidence')
  check(count(native,'effect-decision-ack')==0 and coordinator.closed,'post-RPC drift detaches without ACK or wrong-grant certificate')

print(json.dumps({'passed':True,'checks':len(checks),'nativeAcceptance':False,'scope':'Actual private coordinator/production V7 store; strict schema response doubles, actual file barriers and lock-depth checks. Adversarial reply regression is not claimed as valid native ordering. No real native transport/C/Elm or full proof.'}))
