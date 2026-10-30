"""Actual corrected store faults and persisted-orphan replay; no native/C proof."""
import contextlib,copy,errno,importlib.util,json,os,pathlib,sys,tempfile
from unittest.mock import patch
D=pathlib.Path(__file__).resolve().parents[2];R=pathlib.Path(__file__).resolve().parents[4]
sys.path[:0]=[str(D/'adapter'),str(R/'implementation/warlock/adapter')]
from recovery_store import RecoveryStore
from cancellation_ledger import CancellationLedger
from endpoint import Refused
from workspace_navigation import Navigation
spec=importlib.util.spec_from_file_location('pair',pathlib.Path(__file__).with_name('check_pair_lookup.py'));q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q);f=q.f
checks=[]
def check(value,name):
 if not value:raise AssertionError(name)
 checks.append(name)
def no(fn,name):
 try:fn()
 except (Refused,OSError,ValueError):checks.append(name);return
 raise AssertionError(name+' accepted')
@contextlib.contextmanager
def opened():
 with tempfile.TemporaryDirectory(prefix='warlock-orphan-fault-') as runtime:
  os.chmod(runtime,0o700)
  with RecoveryStore(runtime,'fixture','1',cancellation=True) as store:
   Navigation(store);store.cancellation_attach(f.BOUND)
   yield store

def add_companion(store):
 value=f.intent();record=f.pending(store,value);comp=q.companion(record,'Reserved');q.publish(store,record,comp);return record,comp
for operation in ('required-open','optional-open','read','close'):
 with opened() as store:
  record,comp=add_companion(store);key=f.storage_key(record);before=(pathlib.Path(store.path)/'admissions-v1'/(key+'.json')).read_bytes()
  with store.ledger.host_guard():
   if operation in ('required-open','optional-open'):
    real=os.open
    def bad(name,*args,**kwargs):
     if name=='cancellation-admissions-v1':raise OSError(errno.EIO,'injected companion open')
     return real(name,*args,**kwargs)
    with patch('os.open',bad):no(lambda:store.ledger._companion_directory_locked(required=operation=='required-open'),operation+' refuses')
   elif operation=='read':
    real=store.ledger.raw
    def bad(directory,name,limit):
     if name==key+'.json':raise OSError(errno.EIO,'injected companion read')
     return real(directory,name,limit)
    with patch.object(store.ledger,'raw',bad):no(store.ledger._companion_scan_locked,'scan read refuses')
   else:
    fd=store.ledger._companion_directory_locked();real=os.close
    def bad(value):
     real(value)
     if value==fd:raise OSError(errno.EIO,'injected companion close')
    with patch('os.close',bad):no(lambda:store.ledger._close_companion_locked(fd),'close uncertainty refuses')
  check(store.ledger.poisoned,operation+' poisons shared store')
  no(lambda:store.cancellation_snapshot(f.BOUND),operation+' poisoned lane refuses further access')
  check((pathlib.Path(store.path)/'admissions-v1'/(key+'.json')).read_bytes()==before,operation+' retains exact Pending')
with opened() as store:
 with store.ledger.host_guard():no(lambda:store.ledger._companion_directory_locked(required=True),'expected missing companion refuses')
 check(not store.ledger.poisoned,'missing input alone does not poison store')
# Simulate persisted output of the reproduced old candidate, not a new trusted producer.
for field in ('settled','settlementHistory','latest'):
 with tempfile.TemporaryDirectory(prefix='warlock-orphan-restart-') as runtime:
  os.chmod(runtime,0o700);store=RecoveryStore(runtime,'fixture','1',cancellation=True);Navigation(store);store.cancellation_attach(f.BOUND)
  record,comp=add_companion(store);store.ledger.legacy_reconciliation_records();path=pathlib.Path(store.path);key=f.storage_key(record)
  state=json.loads((path/'ledger-v7.json').read_bytes());definitive={**record,'status':'Refused'}
  if field=='latest':state['legacy']['latest']=definitive
  else:state['legacy'][field].append(definitive)
  store.close();(path/'ledger-v7.json').write_bytes(f.encoded(state));(path/'ledger-v7.json').chmod(0o600)
  before={str(p.relative_to(path)):p.read_bytes() for p in path.rglob('*') if p.is_file()}
  no(lambda:RecoveryStore(runtime,'fixture','1',cancellation=True),'restart refuses companion '+field+' collision')
  after={str(p.relative_to(path)):p.read_bytes() for p in path.rglob('*') if p.is_file()}
  check(before==after,'restart preserves all bytes for '+field)
  check((path/'admissions-v1'/(key+'.json')).exists(),'restart retains Pending for '+field)
# Genuine legacy custody is still eligible when it has no typed companion.
with opened() as store:
 record=f.pending(store,f.intent());check(store.begin(f.BOUND,record['intent'],1),'genuine legacy begin still works')
 outcome={'protocolVersion':3,'kind':'effect-outcome','effectProtocol':1,'binding':f.BOUND,'intent':record['intent'],'status':'Refused','reason':'native-refused','revision':'7','outputGeneration':'5'}
 store.settle(outcome);frames=store.settlement_frames(f.BOUND)
 check(any(row['record']['status']=='Refused' for row in frames),'genuine legacy definitive frame still emitted')
print(json.dumps({'passed':True,'checks':len(checks),'names':checks,'scope':'Actual corrected candidate store EIO/open/read/close poison, persisted corruption restart refusal and genuine legacy positive. No real native producer or C mutation.'}))
