"""Real cache predicate fault controls and independent V7 prerequisite."""
import copy,errno,importlib.util,json,os,pathlib,sys
from unittest.mock import patch
D=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cache_cases',D/'cache.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
# Reuse the actual factories without rerunning the separate retained case group.
f=q.f;Refused=q.Refused;check=q.check;no=q.no
base=len(q.checks)
for operation in ('projection-read','cache-open','cache-file-sync','cache-dir-sync'):
 with q.fixture() as (store,native,coordinator,events,frames):
  rec,comp,wire=q.prepare(store,coordinator);coordinator.handle(q.cf.request('effect-cancel',wire));frame=frames[-1];key=comp['key'];q.persist_cache(store,frame,comp)
  with store.ledger.host_guard():state=store.ledger._current_v7_locked()
  before=q.files(store)
  if operation=='projection-read':
   real=store.ledger.raw
   def bad(directory,name,limit):
    if name==key+'.json' and os.fstat(directory).st_ino==(pathlib.Path(store.path)/'admissions-v1').stat().st_ino:raise OSError(errno.EIO,'injected projection admission read')
    return real(directory,name,limit)
   with patch.object(store.ledger,'raw',bad):no(lambda:store.cancellation_settlement_frames(f.BOUND),'projection I/O refuses')
  elif operation=='cache-open':
   real=os.open
   def bad(name,*args,**kwargs):
    if name=='cancellation-settlements-v1':raise OSError(errno.EIO,'injected cache directory open')
    return real(name,*args,**kwargs)
   with store.ledger.host_guard(),patch('os.open',bad):no(lambda:q.cached_retirement_locked(store.ledger,comp,state),'cache directory I/O refuses')
  else:
   real=os.fsync;directory_inode=(pathlib.Path(store.path)/'cancellation-settlements-v1').stat().st_ino;file_inode=(pathlib.Path(store.path)/'cancellation-settlements-v1'/(key+'.json')).stat().st_ino
   def bad(fd):
    wanted=file_inode if operation=='cache-file-sync' else directory_inode
    if os.fstat(fd).st_ino==wanted:raise OSError(errno.EIO,'injected cache durability barrier')
    return real(fd)
   with store.ledger.host_guard(),patch('os.fsync',bad):no(lambda:q.cached_retirement_locked(store.ledger,comp,state),'cache durability refuses '+operation)
  check(store.ledger.poisoned,'shared lane poisoned '+operation)
  no(lambda:store.cancellation_snapshot(f.BOUND),'poisoned direct read refuses '+operation)
  check(q.files(store)==before,'all persistent bytes preserved '+operation)
# Shape-valid cached proof alone cannot substitute for this store's native certificate.
with q.fixture() as (store,native,coordinator,events,frames):
 rec,comp,wire=q.prepare(store,coordinator);coordinator.handle(q.cf.request('effect-cancel',wire));saved_frame=copy.deepcopy(frames[-1])
with q.fixture() as (store,native,coordinator,events,frames):
 rec,comp=q.publish_pair(store);q.persist_cache(store,saved_frame,comp)
 with store.ledger.host_guard():
  state=store.ledger._current_v7_locked();no(lambda:q.cached_retirement_locked(store.ledger,comp,state),'strict valid cache without current V7 certificate refuses')
 check(store.cancellation_snapshot(f.BOUND)==[],'cache cannot fabricate a V7 native decision')
# A native ACK cache cannot run ahead of the persisted ACK stage.
with q.fixture() as (store,native,coordinator,events,frames):
 rec,comp,wire=q.prepare(store,coordinator)
 with patch.object(native,'ack_effect_decision',side_effect=Refused('transport uncertainty')):no(lambda:coordinator.handle(q.cf.request('effect-cancel',wire)),'actual pending ACK source retained')
 ahead=copy.deepcopy(frames[0]);ahead['ackState']='Acknowledged';ahead['acknowledgement']={k:v for k,v in ahead['certificate'].items() if k not in ('status','reason','revision','outputGeneration')};ahead['acknowledgement']['kind']='effect-decision-acknowledged'
 q.persist_cache(store,ahead,comp)
 with store.ledger.host_guard():
  state=store.ledger._current_v7_locked();no(lambda:q.cached_retirement_locked(store.ledger,comp,state),'strict-valid acknowledged cache cannot outrun durable Pending')
 check(store.cancellation_snapshot(f.BOUND)[0]['ackState']=='Pending','rejected cache leaves ACK custody unchanged')
print(json.dumps({'passed':True,'totalAssertionEventsIncludingRetainedCases':len(q.checks),'newAssertionEvents':len(q.checks)-base,'scope':'Actual Python cache/projection I/O fault poison plus strict-valid cache independent V7/ACK prerequisites; C-writer/native doubles. No actual C cache consumer or native acceptance.'}))
