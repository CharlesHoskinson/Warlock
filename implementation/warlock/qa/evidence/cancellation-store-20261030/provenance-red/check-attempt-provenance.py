"""Independent V7 filesystem/transition regressions; no native or power-loss proof."""
import copy,hashlib,json,os,pathlib,sys,tempfile
sys.path[0:0]=[str(pathlib.Path(__file__).parent/'adapter'),'/home/charles/Warlock/implementation/warlock/adapter']
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
 rec=pending(store,value);reserved=store.cancellation_reserve(BOUND,value,DEADLINE)
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

fixed='--expect-fixed' in sys.argv
observations=[]
for case in ['unattempted-prepare','unattempted-commit']:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-provenance-') as temporary:
  with open_store(pathlib.Path(temporary),'provenanceqa','1') as store:
   if case=='unattempted-prepare':
    rec=pending(store,intent());reserved=store.cancellation_reserve(BOUND,intent(),DEADLINE);key=reserved['record']['key']
    native=Native();native.cancellation_negotiate('1');wire=native.prepare_effect(intent(),DEADLINE)
    proof=_native_cancellation_evidence(rec,DEADLINE,None,wire,phase='initial')
   else:
    key,rec,native,wire=prepared(store,intent())
    response=native.commit_effect(wire)
    proof=_native_cancellation_evidence(rec,DEADLINE,wire['preparedId'],response,phase='established')
   before=(store.path/'ledger-v7.json').read_bytes()
   try:result=store.cancellation_observe(key,proof);accepted=True
   except Refused:accepted=False
   if fixed:check(not accepted and (store.path/'ledger-v7.json').read_bytes()==before,case+' refuses before persistence')
   else:check(accepted,case+' expected private baseline gap reproduced')
   observations.append({'case':case,'acceptedWithoutDurableAttempt':accepted})
print(json.dumps({'passed':True,'expectedDefectReproduced':not fixed,'observations':observations,'scope':'Actual store with strictly correlated native-response doubles supplied out of order; no actual native mutation/transport/daemon bug claimed.'}))
