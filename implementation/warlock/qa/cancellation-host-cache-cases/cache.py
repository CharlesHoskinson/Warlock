"""Actual cache/certificate join and coordinator output; C/native response doubles."""
import contextlib,copy,importlib.util,json,os,pathlib,sys,tempfile
from unittest.mock import patch
D=pathlib.Path(__file__).resolve().parents[2];R=D.parents[1]
sys.path[:0]=[str(D/'adapter'),str(R/'implementation/warlock/adapter'),str(R/'implementation/warlock/qa/cancellation-store-cases')]
from recovery_store import RecoveryStore
from cancellation_ledger import CancellationLedger
from cancellation_coordinator import CancellationCoordinator
from cancellation_host_admission import validate_companion
from cancellation_host_cache import cached_retirement_locked
from cancellation_host_settlement import validate_settlement
from workspace_navigation import Navigation
from endpoint import Refused
import fixture as f
spec=importlib.util.spec_from_file_location('cf',R/'implementation/warlock/qa/cancellation-coordinator-cases/coordinator_fixture.py');cf=importlib.util.module_from_spec(spec);spec.loader.exec_module(cf)
checks=[]
def check(value,name):
 if not value:raise AssertionError(name)
 checks.append(name)
def no(fn,name):
 try:fn()
 except (Refused,OSError,ValueError):checks.append(name);return
 raise AssertionError(name+' accepted')
def write_locked(store,directory,name,value):
 path=pathlib.Path(store.path)/directory
 try:path.mkdir(mode=0o700)
 except FileExistsError:pass
 raw=f.encoded(value);temporary=path/(name+'.tmp');fd=os.open(temporary,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
 try:
  offset=0
  while offset<len(raw):offset+=os.write(fd,raw[offset:])
  os.fsync(fd)
 finally:os.close(fd)
 os.replace(temporary,path/name);fd=os.open(path,os.O_DIRECTORY|os.O_NOFOLLOW)
 try:os.fsync(fd)
 finally:os.close(fd)
 os.fsync(store.fd)
def publish_pair(store,value=None):
 value=value or f.intent();rec=f.pending(store,value);key=f.storage_key(rec)
 companion={'schema':1,'kind':'host-cancellation-admission','state':'Submitted','key':key,'admission':rec,'selection':{'selectionId':key[:32],'scope':{'id':'9','generation':'10'},'publication':'11','lease':'12','controlId':'restore','clock':'CLOCK_MONOTONIC','acceptedMonotonicNs':str(int(f.DEADLINE)-2000000000),'deadlineMonotonicNs':f.DEADLINE}}
 validate_companion(companion)
 with store.ledger.host_guard():write_locked(store,'cancellation-admissions-v1',key+'.json',companion)
 return rec,companion
def persist_cache(store,frame,companion):
 frame=validate_settlement(frame,companion,frame['binding'])
 with store.ledger.host_guard():write_locked(store,'cancellation-settlements-v1',frame['key']+'.json',frame)
def files(store):return {str(p.relative_to(store.path)):p.read_bytes() for p in pathlib.Path(store.path).rglob('*') if p.is_file()}
@contextlib.contextmanager
def fixture(sink_fail=False):
 with tempfile.TemporaryDirectory(prefix='warlock-cache-join-') as runtime:
  os.chmod(runtime,0o700)
  store=RecoveryStore(runtime,'fixture','1',cancellation=True);Navigation(store);events=[];depth=[0];frames=[];original=store.ledger.host_guard
  @contextlib.contextmanager
  def guard():
   with original() as fd:
    depth[0]+=1;check(depth[0]==1,'single host guard')
    try:yield fd
    finally:depth[0]-=1
  store.ledger.host_guard=guard
  def sink(frame):
   check(depth[0]==0,'typed backend output outside host guard');events.append('emit:'+frame['ackState'])
   if sink_fail:raise Refused('injected owned backend output failure')
   frames.append(copy.deepcopy(frame))
  native=cf.Native(events,depth);hello=native.hello();coordinator=CancellationCoordinator(native,store,hello,settlement_sink=sink)
  try:yield store,native,coordinator,events,frames
  finally:coordinator.close();store.close()
def prepare(store,coordinator):
 coordinator.handle(cf.request('effect-cancellation-negotiate'));rec,comp=publish_pair(store);wire=coordinator.handle(cf.request('effect-prepare'));return rec,comp,wire
def run_cases():
 for status in ('Cancelled','Committed','Refused'):
  with fixture() as (store,native,coordinator,events,frames):
   rec,comp,wire=prepare(store,coordinator);check(store.cancellation_settlement_frames(f.BOUND)==[],'Prepared has no typed settlement '+status)
   if status=='Refused':native.state='Refused'
   events.clear();operation='effect-commit' if status=='Committed' else 'effect-cancel';result=coordinator.handle(cf.request(operation,wire))
   check(result['status']==status,'known native schema terminal '+status)
   check([x['ackState'] for x in frames]==['Pending','Acknowledged'],'both actual typed ACK projections '+status)
   check(events.index('emit:Pending')<events.index('rpc:effect-decision-ack')<events.index('emit:Acknowledged'),'typed output precedes native ACK and update follows '+status)
   check(all(x['executionAuthorized'] is False and x['certificate']==result for x in frames),'exact native certificate without execution rights '+status)
   key=comp['key'];pending_path=pathlib.Path(store.path)/'admissions-v1'/(key+'.json');check(not pending_path.exists(),'actual retired Pending before local cache '+status)
   later=f.intent('2','4');new_record=f.pending(store,later)
   no(lambda:store.begin(f.BOUND,later,1),'same target fenced before C cache '+status)
   before_comp=(pathlib.Path(store.path)/'cancellation-admissions-v1'/(key+'.json')).read_bytes()
   persist_cache(store,frames[0],comp)
   check(store.begin(f.BOUND,later,1),'different full key same target admitted only after exact durable cache '+status)
   check((pathlib.Path(store.path)/'cancellation-admissions-v1'/(key+'.json')).read_bytes()==before_comp,'immutable companion retained '+status)
   no(lambda:store.begin(f.BOUND,rec['intent'],1),'old exact key permanently excluded from legacy '+status)
   no(lambda:store.settle({'protocolVersion':3,'kind':'effect-outcome','effectProtocol':1,'binding':f.BOUND,'intent':rec['intent'],'status':'Refused','reason':'native-refused','revision':'7','outputGeneration':'5'}),'old exact key never legacy-settled '+status)
   before=files(store);calls=copy.deepcopy(native.calls)
   req={'protocolVersion':3,'kind':'host-cancellation-receipt-request','cancellationHostProtocol':1,'binding':copy.deepcopy(f.BOUND),'effectProtocol':1,'intent':rec['intent'],'selectionId':comp['selection']['selectionId'],'deadlineMonotonicNs':f.DEADLINE}
   count=len(frames);readback=coordinator.handle(req)
   check(readback['record']['key']==key and len(frames)==count+1,'read-only exact terminal lookup redelivers typed settlement '+status)
   check(files(store)==before and native.calls==calls,'receipt redelivery makes no storage mutation or native call '+status)
   new_binding={**f.BOUND,'session':'99','frontend':'100'};history=store.cancellation_settlement_frames(new_binding)
   check(history[0]['binding']==new_binding and history[0]['admission']['binding']==f.BOUND,'historical delivery preserves original binding '+status)
 with fixture() as (store,native,coordinator,events,frames):
  rec,comp,wire=prepare(store,coordinator);native.reply_mode='unknown';out=coordinator.handle(cf.request('effect-commit',wire))
  check(out['status']=='Unknown' and frames==[],'Unknown never produces a terminal cache receipt')
  check(store.cancellation_settlement_frames(f.BOUND)==[],'Unknown projection empty')
 with fixture(sink_fail=True) as (store,native,coordinator,events,frames):
  rec,comp,wire=prepare(store,coordinator)
  no(lambda:coordinator.handle(cf.request('effect-cancel',wire)),'failed owned output refuses before ACK')
  check(cf.count(native,'effect-decision-ack')==0,'failed pending output sends zero native ACK')
  saved=store.cancellation_snapshot(f.BOUND)[0]
  check(saved['stage']=='AdmissionRetired' and saved['ackState']=='Pending' and coordinator.closed,'output failure preserves known terminal custody and detaches')
 with fixture() as (store,native,coordinator,events,frames):
  rec,comp,wire=prepare(store,coordinator)
  with patch.object(native,'ack_effect_decision',side_effect=Refused('lost native ACK')):no(lambda:coordinator.handle(cf.request('effect-cancel',wire)),'lost native ACK retains pending')
  check(len(frames)==1 and frames[0]['ackState']=='Pending','pre-ACK receipt survives transport uncertainty')
  persist_cache(store,frames[0],comp);store.cancellation_attach(f.BOUND)
  later=f.intent('2','8');rec2,comp2=publish_pair(store,later)
  no(lambda:store.cancellation_reserve(f.BOUND,later,f.DEADLINE),'valid local cache does not bypass durable unACKed native-slot guard')
 with fixture() as (store,native,coordinator,events,frames):
  rec,comp,wire=prepare(store,coordinator);coordinator.handle(cf.request('effect-cancel',wire));key=comp['key']
  persist_cache(store,frames[-1],comp)
  with store.ledger.host_guard():
   state=store.ledger._current_v7_locked();found=cached_retirement_locked(store.ledger,comp,state)
  check(found['ackState']=='Acknowledged','exact stored native ACK cache accepted')
  raw_before=(pathlib.Path(store.path)/'cancellation-admissions-v1'/(key+'.json')).read_bytes()
  bad=copy.deepcopy(frames[-1]);bad['preparedId']='999';bad['certificate']['preparedId']='999';bad['acknowledgement']['preparedId']='999'
  validate_settlement(bad,comp,f.BOUND);check(True,'conflicting preparation cache is internally strict-valid before V7 join')
  with store.ledger.host_guard():write_locked(store,'cancellation-settlements-v1',key+'.json',bad)
  with store.ledger.host_guard():no(lambda:cached_retirement_locked(store.ledger,comp,state),'conflicting cache preparation refuses')
  check((pathlib.Path(store.path)/'cancellation-admissions-v1'/(key+'.json')).read_bytes()==raw_before,'conflicting cache never rewrites companion')
 print(json.dumps({'passed':True,'checks':len(checks),'names':checks,'scope':'Actual new store/coordinator/projection/cache predicate with actual durable files; explicit C-cache-writer and native-response doubles. No actual owning C receiver, native producer or original acceptance.'}))

if __name__=='__main__':run_cases()
