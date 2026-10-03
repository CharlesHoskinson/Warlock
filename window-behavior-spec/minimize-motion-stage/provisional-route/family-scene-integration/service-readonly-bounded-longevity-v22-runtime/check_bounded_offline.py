"""Full inherited proof plus typed current-data/closure models; CPU only."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,time
from check_longevity_offline import MODELS as INHERITED
P=Path(__file__).resolve().parent
MODELS=INHERITED+['bounded_read_authority','readonly_current_close','current_dataset_shape']
EXPECTED_PYTHON=388
EXPECTED_NAMED=383

def main():
 dest=P/'bounded-source-typed-final-offline-checkpoint.json'
 if dest.exists():raise SystemExit('fresh proof destination required')
 env={k:v for k,v in os.environ.items() if k not in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')};env['PYTHONDONTWRITEBYTECODE']='1'
 before={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in P.iterdir() if f.is_file() and f.suffix in ('.py','.qnt','.md')}
 commands=[[sys.executable,'-B','-m','unittest','discover','-s','.','-p','test_*.py','-v']]
 for model in MODELS:
  commands += [['quint','typecheck',model+'_test.qnt'],['quint','test',model+'_test.qnt','--backend=rust','--seed=2026100222'],['quint','run',model+'.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100222','--verbosity=0']]
 commands += [['quint','run','bounded_read_authority.qnt','--step=validStep','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100223','--verbosity=0']]
 checks=[];named=0;python_count=0
 for i,cmd in enumerate(commands):
  log=P/f'bounded-source-typed-final-full-check-{i:02d}.log'
  if log.exists():raise SystemExit('fresh log required')
  begin=time.monotonic()
  # Aggregate observer only; all original product/query/fixture deadlines stay exact.
  with log.open('wb') as stream:
   try:r=subprocess.run(cmd,cwd=P,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=600 if i==0 else 90)
   except subprocess.TimeoutExpired:
    failure={'aggregateObserverTimeout':True,'command':cmd,'log':str(log),'sourceSHA256':before,'nativeLaunch':False}
    (P/'retained-bounded-full-offline-timeout.json').write_text(json.dumps(failure,indent=2)+'\n');raise
  output=log.read_text();checks.append({'command':cmd,'exitCode':r.returncode,'elapsedSeconds':time.monotonic()-begin,'log':str(log),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
  if r.returncode or 'error:' in output:
   (P/'retained-bounded-full-offline-failure.json').write_text(json.dumps({'checks':checks,'sourceSHA256':before,'nativeLaunch':False},indent=2)+'\n')
   raise SystemExit('offline failure: '+str(log))
  if i==0:python_count=int(re.search(r'Ran (\d+) tests',output)[1])
  elif cmd[1]=='test':named+=int(re.search(r'(\d+) passing',output)[1])
  print(json.dumps({'index':i,'python':python_count,'namedSoFar':named,'elapsedSeconds':checks[-1]['elapsedSeconds']}),flush=True)
 assert (python_count,named)==(EXPECTED_PYTHON,EXPECTED_NAMED),(python_count,named)
 assert all(hashlib.sha256(Path(n).read_bytes()).hexdigest()==h for n,h in before.items())
 report={'version':'readonly-bounded-v22','pythonTests':python_count,'quintNamedScenarios':named,'quintModels':len(MODELS),'samplesPerModel':2000,'steps':100,'extraBoundedValidPathSamples':2000,'checks':checks,'sourceSHA256':before,'sourceUnchangedDuringProof':True,'originalQueryControllerFixtureDeadlinesUnchanged':True,'nativeLaunch':False,'nativeBaselineAccepted':False,'currentUserCancellationAccepted':False,'actorLedgerLongevityImplemented':False}
 dest.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'python':python_count,'named':named,'models':len(MODELS),'passed':True}))
if __name__=='__main__':main()
