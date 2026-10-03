"""Formal before runtime; logs and source map are exclusive external evidence."""
import hashlib,json,os,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,data):
 with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(data);f.flush();os.fsync(f.fileno())
def main():
 sources={str(p):{'sha256':sha(p),'mode':p.stat().st_mode&0o7777}for p in B.iterdir()if p.is_file()}
 commands=[['quint','typecheck','housekeeping_admission_test.qnt'],['quint','test','housekeeping_admission_test.qnt','--backend=rust','--seed=2026100226'],['quint','run','housekeeping_admission.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100226','--verbosity=0']];checks=[]
 for i,cmd in enumerate(commands):
  start=time.monotonic();r=subprocess.run(cmd,cwd=B,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90);log=B/('formal-'+str(i)+'.log');save(log,r.stdout);checks.append({'command':cmd,'exitCode':r.returncode,'seconds':time.monotonic()-start,'log':str(log),'sha256':sha(log)})
  if r.returncode:break
 unchanged=all(sha(p)==r['sha256']and Path(p).stat().st_mode&0o7777==r['mode']for p,r in sources.items())
 result={'result':'pass'if len(checks)==3 and all(r['exitCode']==0 for r in checks)and unchanged else'fail','checks':checks,'namedScenarios':26,'samples':2000,'steps':100,'sources':sources,'sourceUnchangedDuringFormal':unchanged,'runtimeApplied':False,'nativeAccepted':False,'scope':Path('/proc/self/cgroup').read_text().strip()}
 save(B/'formal-before-runtime.json',(json.dumps(result,indent=2)+'\n').encode());print(json.dumps({k:v for k,v in result.items()if k not in ('sources','checks')}));raise SystemExit(0 if result['result']=='pass'else 1)
if __name__=='__main__':main()
