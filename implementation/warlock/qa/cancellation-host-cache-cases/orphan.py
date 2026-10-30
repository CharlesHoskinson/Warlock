import argparse,copy,importlib.util,json,os,pathlib,sys,tempfile
p=argparse.ArgumentParser();p.add_argument('--adapter',default=str(pathlib.Path(__file__).resolve().parents[2]/'adapter'));p.add_argument('--expect-bug',action='store_true');args=p.parse_args()
R=pathlib.Path(__file__).resolve().parents[4];sys.path[:0]=[args.adapter,str(R/'implementation/warlock/adapter')]
from recovery_store import RecoveryStore
from cancellation_ledger import CancellationLedger
from cancellation_host_admission import validate_companion
from workspace_navigation import Navigation
spec=importlib.util.spec_from_file_location('f',R/'implementation/warlock/qa/cancellation-store-cases/fixture.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
checks=[]
def check(v,name):
 if not v:raise AssertionError(name)
 checks.append(name)
def files(store):return {str(p.relative_to(store.path)):p.read_bytes() for p in pathlib.Path(store.path).rglob('*') if p.is_file()}
with tempfile.TemporaryDirectory(prefix='warlock-orphan-proof-') as runtime:
 os.chmod(runtime,0o700)
 with RecoveryStore(runtime,'orphanqa','1',cancellation=True) as store:
  Navigation(store);store.cancellation_attach(f.BOUND);value=f.intent();rec=f.pending(store,value);key=f.storage_key(rec)
  companion={'schema':1,'kind':'host-cancellation-admission','state':'Reserved','key':key,'admission':rec,'selection':{'selectionId':'a'*32,'scope':{'id':'9','generation':'10'},'publication':'11','lease':'12','controlId':'restore','clock':'CLOCK_MONOTONIC','acceptedMonotonicNs':str(int(f.DEADLINE)-2000000000),'deadlineMonotonicNs':f.DEADLINE}}
  validate_companion(companion,submitted=False)
  with store.ledger.host_guard():
   directory=pathlib.Path(store.path)/'cancellation-admissions-v1';directory.mkdir(mode=0o700);target=directory/(key+'.json');fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
   try:
    data=f.encoded(companion);offset=0
    while offset<len(data):offset+=os.write(fd,data[offset:])
    os.fsync(fd)
   finally:os.close(fd)
   fd=os.open(directory,os.O_DIRECTORY)
   try:os.fsync(fd)
   finally:os.close(fd)
  check(store.cancellation_snapshot(f.BOUND)==[],'orphan has no typed V7 registration')
  projection=store.ledger.legacy_reconciliation_records();projected=any(f.storage_key(row)==key for row in projection)
  check(projected==args.expect_bug,'legacy projection disposition matches expected defect/fix')
  before=files(store)
  legacy={'protocolVersion':3,'kind':'effect-outcome','effectProtocol':1,'binding':copy.deepcopy(f.BOUND),'intent':copy.deepcopy(value),'status':'Refused','reason':'native-refused','revision':'7','outputGeneration':'5'}
  refused=False
  try:store.settle(legacy)
  except f.Refused:refused=True
  if args.expect_bug:
   check(not refused,'baseline accepts legacy definitive outcome for companion-only key')
   frames=store.settlement_frames(f.BOUND)
   check(any(row['kind']=='host-admission-settled' and f.storage_key(row['record'])==key and row['record']['status']=='Refused' for row in frames),'baseline emits legacy settlement for companion custody')
   check(store.cancellation_snapshot(f.BOUND)==[],'unsafe legacy frame has no native cancellation certificate')
  else:
   check(refused,'corrected store rejects companion legacy settlement')
   check(files(store)==before,'refused settlement preserves every data byte')
   check(not any(f.storage_key(row['record'])==key for row in store.settlement_frames(f.BOUND)),'corrected store emits no legacy settlement for orphan')
  check((pathlib.Path(store.path)/'admissions-v1'/(key+'.json')).exists(),'actual Pending file preserved; no C receiver execution claimed')
print(json.dumps({'passed':True,'defectReproduced':args.expect_bug,'checks':len(checks),'names':checks,'scope':'Actual candidate V7 projection/settle/settlement_frames and durable Reserved+Pending. Full legacy response schema supplied; no actual native producer or C receiver mutation observed.'}))
