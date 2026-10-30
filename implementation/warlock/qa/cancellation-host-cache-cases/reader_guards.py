import argparse,contextlib,importlib.util,json,os,pathlib,sys,tempfile
p=argparse.ArgumentParser();p.add_argument('--adapter',default=str(pathlib.Path(__file__).resolve().parents[2]/'adapter'));p.add_argument('--expect-bug',action='store_true');a=p.parse_args();R=pathlib.Path(__file__).resolve().parents[4]
sys.path[:0]=[a.adapter,str(R/'implementation/warlock/adapter')]
from recovery_store import RecoveryStore
from cancellation_ledger import CancellationLedger
from workspace_navigation import Navigation
spec=importlib.util.spec_from_file_location('f',R/'implementation/warlock/qa/cancellation-store-cases/fixture.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
observations={}
with tempfile.TemporaryDirectory(prefix='warlock-reader-guard-') as runtime:
 os.chmod(runtime,0o700)
 with RecoveryStore(runtime,'fixture','1',cancellation=True) as store:
  Navigation(store);store.cancellation_attach(f.BOUND)
  original_guard=store.ledger.host_guard;original_scan=store.ledger._companion_scan_locked;depth=[0];seen=[]
  @contextlib.contextmanager
  def tracked():
   with original_guard() as directory:
    depth[0]+=1
    try:yield directory
    finally:depth[0]-=1
  def scan():seen.append(depth[0]);return original_scan()
  store.ledger.host_guard=tracked;store.ledger._companion_scan_locked=scan
  for name,call in [('snapshot',lambda:store.read('intent.json')),('recover',lambda:store.recovery_frames(f.BOUND)),('blocked',lambda:store.ledger.blocked('1','4'))]:
   seen.clear();call();assert seen,name+' did not exercise actual mutable companion scan'
   observations[name]=list(seen)
   if a.expect_bug:assert 0 in seen,name+' no longer reproduces missing guard'
   else:assert all(level==1 for level in seen),name+' lacks exactly one guard'
  assert depth==[0]
print(json.dumps({'passed':True,'defectReproduced':a.expect_bug,'observedHostGuardDepths':observations,'scope':'Actual public read/recovery/blocked entrypoints and production companion scans. No actual adversarial concurrent write schedule executed.'}))
