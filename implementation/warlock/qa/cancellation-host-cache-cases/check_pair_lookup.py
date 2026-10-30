"""Private source-only actual V7/lookup proposal. Not run; no compositor evidence."""
import copy, importlib.util, json, os, pathlib, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(HERE/'adapter'), str(ROOT/'implementation/warlock/adapter')]
# Load the private candidates before the existing fixture adjusts sys.path.
from recovery_store import RecoveryStore
from cancellation_coordinator import CancellationCoordinator
from cancellation_host_admission import validate_companion
from admission_ledger import storage_key
from durable_ledger import encoded
from endpoint import Refused
from workspace_navigation import Navigation
spec=importlib.util.spec_from_file_location('f',ROOT/'implementation/warlock/qa/cancellation-store-cases/fixture.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

def refuse(fn):
    try: fn()
    except (Refused, OSError, ValueError): return
    raise AssertionError('expected refusal')

def companion(rec, state='Submitted'):
    return {'schema':1,'kind':'host-cancellation-admission','state':state,'key':storage_key(rec),
      'admission':copy.deepcopy(rec),'selection':{'selectionId':'a'*32,'scope':{'id':'9','generation':'10'},
      'publication':'11','lease':'12','controlId':'restore','clock':'CLOCK_MONOTONIC',
      'acceptedMonotonicNs':str(int(f.DEADLINE)-2000000000),'deadlineMonotonicNs':f.DEADLINE}}

def publish(store, rec, value):
    with store.ledger.host_guard():
        try: os.mkdir('cancellation-admissions-v1',0o700,dir_fd=store.fd)
        except FileExistsError: pass
        directory=os.open('cancellation-admissions-v1',os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=store.fd)
        try:
            fd=os.open(storage_key(rec)+'.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=directory)
            try:
                data=encoded(value); offset=0
                while offset<len(data): offset+=os.write(fd,data[offset:])
                os.fsync(fd)
            finally: os.close(fd)
            os.fsync(directory);os.fsync(store.fd)
        finally:os.close(directory)

def main():
  with tempfile.TemporaryDirectory(prefix='warlock-host-pair-') as runtime:
    os.chmod(runtime,0o700)
    with RecoveryStore(runtime,'fixture','1',cancellation=True) as store:
      Navigation(store); client=f.Native()
      coordinator=CancellationCoordinator(client,store,{'protocolVersion':3,'kind':'attached','binding':copy.deepcopy(f.BOUND)},settlement_sink=lambda frame:None)
      value=f.intent(); request={'protocolVersion':3,'kind':'host-cancellation-receipt-request',
        'cancellationHostProtocol':1,'binding':copy.deepcopy(f.BOUND),'effectProtocol':1,
        'intent':copy.deepcopy(value),'selectionId':'a'*32,'deadlineMonotonicNs':f.DEADLINE}
      def files():
        root=pathlib.Path(store.path)
        return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
      before=files()
      response=coordinator.handle(request);assert response['record'] is None and response['executionAuthorized'] is False
      assert files()==before and client.calls==[] and store.cancellation_snapshot(f.BOUND)==[]
      record=f.pending(store,value)
      refuse(lambda:store.cancellation_reserve(f.BOUND,value,f.DEADLINE))
      assert store.cancellation_snapshot(f.BOUND)==[] and client.calls==[]
      publish(store,record,companion(record))
      result=store.cancellation_reserve(f.BOUND,value,f.DEADLINE);assert result['submitPrepare'] is True
      duplicate=store.cancellation_reserve(f.BOUND,value,f.DEADLINE);assert duplicate['submitPrepare'] is False
      found=coordinator.handle(request);assert found['record']['key']==storage_key(record)
      assert found['record']['deadlineMonotonicNs']==f.DEADLINE and client.calls==[]
      found['record']['admission']['intent']['request']='999'
      assert coordinator.handle(request)['record']['admission']['intent']['request']=='1'
      refuse(lambda:store.cancellation_receipt_lookup(f.BOUND,value,f.DEADLINE,'b'*32))
      refuse(lambda:store.cancellation_receipt_lookup(f.BOUND,value,str(int(f.DEADLINE)-1),'a'*32))
      bad=copy.deepcopy(request);bad['binding']['frontend']='4';refuse(lambda:coordinator.handle(bad))
      bad=copy.deepcopy(request);bad['effectProtocol']=True;refuse(lambda:coordinator.handle(bad))
      bad=copy.deepcopy(request);bad['extra']=1;refuse(lambda:coordinator.handle(bad))
      # Same target, distinct request/generation cannot bypass companion custody.
      other=f.intent('2','4');refuse(lambda:store.begin(f.BOUND,other,1))
      assert client.calls==[]
      coordinator.close()
  print(json.dumps({'scope':'private V7 pair and read-only coordinator; response doubles, no native','passed':True}))
if __name__=='__main__':main()
