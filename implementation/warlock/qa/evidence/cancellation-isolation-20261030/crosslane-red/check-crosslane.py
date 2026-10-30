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

from grant_endpoint import GrantEndpoint
from retirement_ledger import ObservationJoin,release_payload
from reconciliation import Reconciliation
CURRENT={**BOUND,'frontend':'4'}
class Retired(GrantEndpoint):
 def __init__(self):self.bound=copy.deepcopy(CURRENT);self._grant_watermarks={};self.calls=[]
 def request(self,payload):
  self.calls.append(copy.deepcopy(payload))
  return {'protocolVersion':3,'kind':'binding-retirement','retirementProtocol':1,'operation':'retire','binding':copy.deepcopy(self.bound),'queriedBinding':copy.deepcopy(payload['queriedBinding']),'requestId':payload['requestId'],'sequence':str(len(self.calls)),'grantState':'Retired'}
def join_for(client,row):
 proof=client.retire(str(len(client.calls)+1),row['binding']);join=ObservationJoin(row,proof)
 for domain,rid,rev in [('action','11','6'),('geometry','12','7')]:
  join.expect(domain,rid);join.accept(domain,rid,CURRENT,{'lifetime':'1','epoch':'4','output':'5','revision':rev})
 return join
fixed='--expect-fixed' in sys.argv
results=[]
for typed in [False,True]:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-crosslane-') as temporary:
  root=pathlib.Path(temporary)
  with open_store(root,'crosslaneqa','1') as store:
   if typed:key,original,native,wire=prepared(store,intent())
   else:
    original=pending(store,intent());check(store.begin(BOUND,intent(),1),'legacy positive begins durably')
   admission_path=store.path/'admissions-v1'/(storage_key(original)+'.json');original_bytes=admission_path.read_bytes()
  with RecoveryStore(root,'crosslaneqa','1',cancellation=True) as reopened:
   row=reopened.ledger.snapshot()['entries'][0];check(row['status']=='Unknown','restart provides valid historical Unknown')
   client=Retired();frames=[];reconciliation=Reconciliation(client,reopened.ledger,frames.append)
   reconciliation.announce();projection_calls=len(client.calls)
   rejected=False
   if reconciliation.pending:
    proof=reconciliation.active
    reconciliation.proof_ready({'protocolVersion':3,'kind':'reconciliation-ready','binding':copy.deepcopy(CURRENT),'proofRequestId':proof.request_id,'queriedBinding':proof.queried_binding.as_dict()})
    for domain,rid in [('action','11'),('geometry','12')]:reconciliation.requested_read(domain,rid)
    try:
     reconciliation.delivered_read('action','11',{'lifetime':'1','epoch':'4','output':'5','revision':'6'})
     reconciliation.delivered_read('geometry','12',{'lifetime':'1','epoch':'4','output':'5','revision':'7'})
    except Refused:rejected=True
   disk=json.loads((reopened.path/'ledger-v7.json').read_bytes())
   if not typed:
    check(not rejected and not admission_path.exists() and disk['legacy']['releases'][0]['phase']=='Released','genuine legacy Unknown proof/read release remains functional')
   elif not fixed:
    check(rejected and not admission_path.exists() and disk['legacy']['releases'][0]['phase']=='Prepared' and disk['cancellations'][0]['certificate'] is None,'expected RED: typed admission unlinked before absent-certificate rejection')
   else:
    check(projection_calls==0 and not reconciliation.pending,'typed rows never enter legacy retirement announcement')
    check(admission_path.read_bytes()==original_bytes and disk['legacy']['releases']==[],'typed projection preserves Pending bytes and release history')
    before=(reopened.path/'ledger-v7.json').read_bytes()
    refused(lambda:reopened.ledger.release(join_for(client,row)),'direct typed legacy release refuses before save/unlink')
    check(admission_path.read_bytes()==original_bytes and (reopened.path/'ledger-v7.json').read_bytes()==before,'direct rejection preserves all durable facts')
    with reopened.ledger.host_guard() as directory:
     refused(lambda:reopened.ledger._remove_admission(directory,row),'central legacy unlink refuses typed key')
    check(admission_path.read_bytes()==original_bytes,'central unlink refusal leaves exact original Pending')
   results.append({'typed':typed,'legacyRetireCallsAtAnnounce':projection_calls,'admissionExists':admission_path.exists(),'rejectedAfterReads':rejected})
print(json.dumps({'passed':True,'expectedDefectReproduced':not fixed,'checks':len(checks),'results':results,'nativeAcceptance':False,'scope':'Actual V7/Reconciliation/legacy release, strict retirement-schema response double and accepted ObservationJoin; no real native producer or mutation proof.'}))
