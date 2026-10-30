from fixture import *
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
fixed=True
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

from retirement_ledger import RetirementLedger
for case in ['parent-bypass','corrupt-replay','different-key-same-target']:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-crosslane-extra-') as temporary:
  root=pathlib.Path(temporary)
  with open_store(root,'crosslaneextraqa','1') as store:
   key,original,native,wire=prepared(store,intent())
   if case=='different-key-same-target':
    terminal(store,key,original,native,wire,'cancel');known=store.cancellation_snapshot(BOUND)[0]
    host_cached_retirement(store,key)
    later=intent('2');new_record=pending(store,later);check(store.begin(BOUND,later,1),'different full key can begin after certified typed retirement')
   admission_path=store.path/'admissions-v1'/(storage_key(new_record if case=='different-key-same-target' else original)+'.json');old_bytes=admission_path.read_bytes()
  store=RecoveryStore(root,'crosslaneextraqa','1',cancellation=True)
  row=store.ledger.snapshot()['entries'][0];client=Retired();join=join_for(client,row)
  before=(store.path/'ledger-v7.json').read_bytes()
  if case=='parent-bypass':
   refused(lambda:RetirementLedger.release(store.ledger,join),'parent legacy release cannot bypass V7 candidate validation')
   check(admission_path.read_bytes()==old_bytes and (store.path/'ledger-v7.json').read_bytes()==before,'decoder collision rejection precedes persistent Prepared release and unlink')
   store.close()
  elif case=='corrupt-replay':
   state=json.loads(before);payload=release_payload(join.record,join.proof,join.observation());state['legacy']['releases'].append(dict(payload,id=hashlib.sha256(encoded(payload)).hexdigest(),phase='Prepared'))
   (store.path/'ledger-v7.json').write_bytes(encoded(state));store.close()
   refused(lambda:RecoveryStore(root,'crosslaneextraqa','1',cancellation=True),'reopen rejects corrupt legacy Prepared collision before replay')
   check(admission_path.read_bytes()==old_bytes,'corrupt replay cannot unlink typed Pending')
  else:
   released=store.ledger.release(join)
   check(released['phase']=='Released' and not admission_path.exists(),'same incarnation with different full legacy key releases normally')
   check(store.cancellation_snapshot(BOUND)[0]==known,'different legacy key release leaves typed certificate history unchanged')
   store.close()

# Existing default V6 fallback must keep its actual retirement/read-join route.
with tempfile.TemporaryDirectory(prefix='warlock-v6-release-control-') as temporary:
 root=pathlib.Path(temporary)
 with RecoveryStore(root,'defaultreleaseqa','1') as store:
  record=pending(store,intent());check(store.begin(BOUND,intent(),1),'default V6 control begins normally')
  path=store.path/'admissions-v1'/(storage_key(record)+'.json')
 with RecoveryStore(root,'defaultreleaseqa','1') as store:
  rows=store.ledger.snapshot()['entries'];client=Retired();join=join_for(client,rows[0])
  release=store.ledger.release(join)
  check(release['phase']=='Released' and not path.exists(),'default V6 positive release still retires exact admission')
  check(not (store.path/'ledger-v7.json').exists(),'default V6 positive never selects V7')
print(json.dumps({'passed':True,'checks':len(checks),'nativeAcceptance':False,'scope':'Actual V7 legacy-isolation and default V6 positive, strict retirement-proof/accepted-read doubles; no actual native producer/mutation proof.'}))
