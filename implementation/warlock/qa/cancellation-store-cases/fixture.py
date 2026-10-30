"""Independent V7 filesystem/transition regressions; no native or power-loss proof."""
import copy,hashlib,json,os,pathlib,sys,tempfile
sys.path[0:0]=[str(pathlib.Path(__file__).resolve().parents[2]/'adapter')]
from recovery_store import RecoveryStore
from delivery_ledger import DeliveryLedger
from admission_ledger import storage_key
from durable_ledger import encoded
from recovery_journal import validate
from endpoint import Refused
from cancellation_ledger import _native_cancellation_evidence
from effect_endpoint import Endpoint
from workspace_navigation import Navigation

def open_store(runtime,instance,lifetime):
 store=RecoveryStore(runtime,instance,lifetime,cancellation=True)
 Navigation(store)
 store.cancellation_attach(BOUND)
 return store
BOUND={'lifetime':'1','session':'2','frontend':'3'}
DEADLINE='18446744073709551615'
checks=[]
def check(value,name):
 if not value:raise AssertionError(name)
 checks.append(name)
def refused(fn,name):
 try:fn()
 except (Refused,OSError,ValueError):checks.append(name);return
 raise AssertionError(name+' accepted')
def intent(request='1',target='4'):
 return {'request':request,'generation':request,'incarnation':target,'operation':'restore','context':{'lifetime':'1','epoch':'3','output':'5','revision':'6'}}
def admission(value):return {'schema':2,'effectProtocol':1,'binding':copy.deepcopy(BOUND),'intent':copy.deepcopy(value),'status':'Pending'}
def pending(store,value):
 record=admission(value);body=encoded(record)
 with store.ledger.host_guard() as directory:
  name=storage_key(record)+'.json';fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=directory)
  try:
   offset=0
   while offset<len(body):offset+=os.write(fd,body[offset:])
   os.fsync(fd)
  finally:os.close(fd)
  os.fsync(directory)
 return record
def cancellation_pending(store,value):
 """Explicit durable host-writer double for the mandatory new pair, not legacy."""
 rec=pending(store,value);identifier=storage_key(rec)
 companion={'schema':1,'kind':'host-cancellation-admission','state':'Submitted','key':identifier,'admission':copy.deepcopy(rec),'selection':{'selectionId':identifier[:32],'scope':{'id':'9','generation':'10'},'publication':'11','lease':'12','controlId':'restore','clock':'CLOCK_MONOTONIC','acceptedMonotonicNs':str(int(DEADLINE)-2000000000),'deadlineMonotonicNs':DEADLINE}}
 from cancellation_host_admission import validate_companion
 validate_companion(companion)
 with store.ledger.host_guard():
  directory=pathlib.Path(store.path)/'cancellation-admissions-v1'
  try:directory.mkdir(mode=0o700)
  except FileExistsError:pass
  fd=os.open(directory/(identifier+'.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  try:
   body=encoded(companion);offset=0
   while offset<len(body):offset+=os.write(fd,body[offset:])
   os.fsync(fd)
  finally:os.close(fd)
  fd=os.open(directory,os.O_DIRECTORY|os.O_NOFOLLOW)
  try:os.fsync(fd)
  finally:os.close(fd)
  os.fsync(store.fd)
 return rec

def host_cached_retirement(store,identifier):
 """Explicit C-cache-writer double after an actual typed producer projection."""
 from cancellation_host_settlement import validate_settlement
 frames=[frame for frame in store.cancellation_settlement_frames(BOUND) if frame['key']==identifier]
 check(len(frames)==1,'actual typed producer supplies exact cache receipt')
 companion=json.loads((pathlib.Path(store.path)/'cancellation-admissions-v1'/(identifier+'.json')).read_bytes())
 frame=validate_settlement(frames[0],companion,BOUND)
 with store.ledger.host_guard():
  directory=pathlib.Path(store.path)/'cancellation-settlements-v1'
  try:directory.mkdir(mode=0o700)
  except FileExistsError:pass
  path=directory/(identifier+'.json');fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  try:
   body=encoded(frame);offset=0
   while offset<len(body):offset+=os.write(fd,body[offset:])
   os.fsync(fd)
  finally:os.close(fd)
  fd=os.open(directory,os.O_DIRECTORY|os.O_NOFOLLOW)
  try:os.fsync(fd)
  finally:os.close(fd)
  os.fsync(store.fd)
 return frame

class Native(Endpoint):
 """Explicit strict-client native response double, never compositor evidence."""
 def __init__(self):self.bound=copy.deepcopy(BOUND);self.state='Prepared';self.prepared=None;self.calls=[]
 def request(self,payload):
  self.calls.append(copy.deepcopy(payload));kind=payload['kind']
  if kind=='effect-cancellation-negotiate':return {'protocolVersion':3,'kind':'effect-cancellation-capabilities','binding':copy.deepcopy(self.bound),'requestId':payload['requestId'],'cancellationProtocol':1,'effectProtocol':1,'operations':['restore'],'maxPreparedPerSession':1,'maxPreparedGlobal':64,'deadlineClock':'CLOCK_MONOTONIC'}
  common={'protocolVersion':3,'cancellationProtocol':1,'effectProtocol':1,'binding':copy.deepcopy(self.bound),'intent':copy.deepcopy(payload['intent']),'preparedId':payload.get('preparedId','41'),'deadlineMonotonicNs':payload['deadlineMonotonicNs']}
  if kind=='effect-prepare':self.prepared={**common,'kind':'effect-prepared'};return copy.deepcopy(self.prepared)
  if kind=='effect-commit':self.state='Committed'
  if kind=='effect-cancel' and self.state=='Prepared':self.state='Cancelled'
  if kind=='effect-decision-request' and self.state=='Prepared':return copy.deepcopy(self.prepared)
  if kind=='effect-decision-ack':return {**common,'kind':'effect-decision-acknowledged'}
  return {**common,'kind':'effect-outcome','status':self.state,'reason':{'Committed':'applied','Cancelled':'cancelled-before-commit','Refused':'dependency-mismatch','Unknown':'effect-unproven'}[self.state],'revision':'7','outputGeneration':'5'}

def prepared(store,value):
 rec=cancellation_pending(store,value);reserved=store.cancellation_reserve(BOUND,value,DEADLINE)
 check(reserved['submitPrepare'] is True,'new reservation is durable before first prepare permission')
 key=reserved['record']['key'];store.cancellation_attempt(key,'prepare')
 native=Native();native.cancellation_negotiate('1');wire=native.prepare_effect(value,DEADLINE)
 proof=_native_cancellation_evidence(rec,DEADLINE,None,wire,phase='initial')
 result=store.cancellation_observe(key,proof)
 check(result['stage']=='Prepared','native prepared observation persists')
 return key,rec,native,wire

def terminal(store,key,rec,native,wire,kind='cancel'):
 store.cancellation_attempt(key,kind);outcome=(native.cancel_effect if kind=='cancel' else native.commit_effect)(wire)
 proof=_native_cancellation_evidence(rec,DEADLINE,wire['preparedId'],outcome,phase='established')
 saved=store.cancellation_observe(key,proof)
 check(saved['stage']=='TerminalStored' and saved['certificate'] is not None,'full known native certificate stored before release')
 before=pathlib.Path(store.path)/'admissions-v1'/(storage_key(rec)+'.json')
 check(before.exists(),'terminal save alone retains original pending file')
 result=store.cancellation_finish(key)
 check(result['stage']=='AdmissionRetired' and not before.exists(),'exact admission retirement follows durable certificate')
 cert=store.cancellation_ack_pending(key);check(cert==outcome,'ACK permission returns exact stored terminal')
 ack=native.ack_effect_decision(cert);result=store.cancellation_acknowledged(key,ack)
 check(result['ackState']=='Acknowledged','only exact acknowledged certificate finishes ACK state')
 return outcome


__all__=[name for name in globals() if not name.startswith('_')]+['_native_cancellation_evidence']
