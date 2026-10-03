"""Source-only full retained and binding model replay; no desktop activity."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,re,subprocess,time
B=Path(__file__).parent
models=['helper_lifecycle','query_lifecycle','capture_lifecycle','service_queries','reversal','service_restart','recovery_collection','actual_service_binding']
source={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in B.glob('*.qnt')}
def run(name):
 test=B/(name+'_test.qnt');test=test if test.exists() else B/(name+'.qnt');base=B/(name+'.qnt');invariant='allProps' if name in ('service_restart','recovery_collection','actual_service_binding') else 'invariant'
 commands=[['quint','typecheck',str(test)],['quint','test',str(test),'--backend=rust','--seed=2026100304'],['quint','run',str(base),'--invariant='+invariant,'--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100304','--verbosity=1']]
 rows=[]
 for i,command in enumerate(commands):
  before=time.monotonic_ns();r=subprocess.run(command,cwd=B,text=True,capture_output=True,timeout=60);log=B/('v4-final-'+name+'-'+str(i)+'.log');log.write_text(r.stdout+r.stderr)
  rows.append({'command':command,'exitCode':r.returncode,'log':str(log),'logSHA256':hashlib.sha256(log.read_bytes()).hexdigest(),'elapsedNs':time.monotonic_ns()-before,'named':int(re.search(r'(\d+) passing',r.stdout).group(1)) if i==1 and re.search(r'(\d+) passing',r.stdout) else 0})
  if r.returncode:break
 return {'model':name,'checks':rows}
with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(run,models))
row={'result':'pass' if all(len(r['checks'])==3 and all(c['exitCode']==0 for c in r['checks']) for r in results) else 'fail','models':len(results),'named':sum(c['named'] for r in results for c in r['checks']),'samplesPerModel':2000,'stepsPerSample':100,'sourceSHA256':source,'sourceUnchanged':source=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in B.glob('*.qnt')},'results':results,'nativeLaunch':False}
path=B/'v4-final-formal-report.json';assert not path.exists();path.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({k:row[k] for k in ('result','models','named','sourceUnchanged')}));raise SystemExit(row['result']!='pass' or not row['sourceUnchanged'])
