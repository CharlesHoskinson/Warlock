import hashlib,json,os,re,stat,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from qa_launch import require_qa_scope
def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def main():
 scope=require_qa_scope();paths=[HERE/'hidden_capture.qnt',HERE/'hidden_capture_test.qnt',HERE/'CONTRACT.md',HERE/'SOURCE_MAPPING.md',Path(__file__)];sources={str(p):stamp(p)for p in paths}
 names=re.findall(r'^ run ([A-Za-z0-9_]+)=',(HERE/'hidden_capture_test.qnt').read_text(),re.M);assert len(names)==23
 cmds=[['quint','typecheck','hidden_capture_test.qnt'],['quint','test','hidden_capture_test.qnt','--match=^('+'|'.join(names)+')$','--backend=rust','--seed=2026100229'],['quint','run','hidden_capture.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100229','--verbosity=0']];rows=[]
 for i,cmd in enumerate(cmds):
  p=HERE/('formal-'+str(i)+'.log');start=time.monotonic()
  with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:r=subprocess.run(cmd,cwd=HERE,stdout=f,stderr=subprocess.STDOUT,timeout=60)
  rows.append({'command':cmd,'exitCode':r.returncode,'seconds':time.monotonic()-start,'log':str(p),**stamp(p)})
  if r.returncode:break
 passed=len(rows)==3 and all(r['exitCode']==0 for r in rows)
 if passed:
  log=(HERE/'formal-1.log').read_text();passed='23 passing' in log and all('ok '+n+' passed' in log for n in names)
 assert sources=={str(p):stamp(p)for p in paths}
 row={'result':'pass'if passed else 'fail','scope':scope,'checks':rows,'namedActuallyRun':23,'names':names,'samples':2000,'steps':100,'sources':sources,'runtimeApplied':False}
 with os.fdopen(os.open(HERE/'formal-before-runtime.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'result':row['result'],'namedActuallyRun':23,'report':str(HERE/'formal-before-runtime.json')}));return int(not passed)
if __name__=='__main__':raise SystemExit(main())
