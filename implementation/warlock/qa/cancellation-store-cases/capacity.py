from fixture import *
from unittest.mock import patch
import cancellation_ledger as ledger_module
from cancellation_endpoint import _REFUSALS
BaseNative=Native
class Native(BaseNative):
 reason='dependency-mismatch'
 def request(self,payload):
  result=super().request(payload)
  if result['kind'] in ('effect-prepared','effect-outcome','effect-decision-acknowledged'):result['preparedId']=DEADLINE
  if result['kind']=='effect-outcome':
   result['revision']=DEADLINE;result['outputGeneration']=DEADLINE
   if result['status']=='Refused':result['reason']=self.reason
  return result
import fixture
fixture.Native=Native
for status,reason in [('Committed','applied'),('Cancelled','cancelled-before-commit'),*[('Refused',x) for x in sorted(_REFUSALS)]]:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-size-envelope-') as temporary:
  with open_store(pathlib.Path(temporary),'capacityqa','1') as store:
   key,rec,native,wire=prepared(store,intent())
   original=json.loads((store.path/'ledger-v7.json').read_bytes());budget=ledger_module._reserved_envelope_bytes(original)
   native.reason=reason
   if status=='Refused':native.state='Refused'
   terminal(store,key,rec,native,wire,'commit' if status=='Committed' else 'cancel')
   final=json.loads((store.path/'ledger-v7.json').read_bytes())
   check(len(encoded(final))<=budget,'actual maximum-counter '+status+'/'+reason+' grows within admitted envelope')
   check(final['cancellations'][0]['certificate']['response']['preparedId']==DEADLINE,'maximum preparation identity retained '+status+'/'+reason)
# Exact funded boundary uses identical immutable scope/input and empty predecessor.
for offset in [0,-1]:
 with tempfile.TemporaryDirectory(prefix='warlock-v7-capacity-boundary-') as temporary:
  with open_store(pathlib.Path(temporary),'capacityqa','1') as store:
   rec=pending(store,intent());before=(store.path/'ledger-v7.json').read_bytes()
   with patch.object(ledger_module,'_LIMIT',budget+offset):
    if offset==-1:
     refused(lambda:store.cancellation_reserve(BOUND,intent(),DEADLINE),'one-byte-under funded envelope refuses before submit permission')
     check((store.path/'ledger-v7.json').read_bytes()==before,'capacity refusal does not change durable cursor/entry')
    else:
     reserved=store.cancellation_reserve(BOUND,intent(),DEADLINE)
     check(reserved['submitPrepare'] is True,'exact funded byte boundary grants first prepare permission')
     prior=(store.path/'ledger-v7.json').read_bytes();other=intent('2','8');pending(store,other)
     refused(lambda:store.begin(BOUND,other,1),'unrelated legacy write cannot spend reserved terminal credit')
     check((store.path/'ledger-v7.json').read_bytes()==prior,'rejected unrelated write retains funded reservation and cursors')
print(json.dumps({'passed':True,'checks':len(checks),'terminalPairs':2+len(_REFUSALS),'nativeAcceptance':False,'scope':'Actual maximum-counter finite strict-terminal pairs, exact funded byte boundary and unrelated legacy write exclusion; strict response doubles, not all64slot/hardware ENOSPC or native proof.'}))
