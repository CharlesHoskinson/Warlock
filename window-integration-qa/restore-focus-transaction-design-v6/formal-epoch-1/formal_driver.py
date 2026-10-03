import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
QA=HERE.parent
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope

def stamp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mode':stat.S_IMODE(p.stat().st_mode)}
def save(path,row):
 with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def main():
 scope=require_qa_scope()
 paths=[p for p in HERE.iterdir() if p.suffix in ('.qnt','.py','.md','.proposed','.patch','.json')]
 sources={str(p):stamp(p) for p in paths}
 cmds=[['quint','typecheck','focus_transaction_test.qnt'],['quint','test','focus_transaction_test.qnt','--backend=rust','--seed=2026100228'],['quint','run','focus_transaction.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--backend=rust','--seed=2026100228','--verbosity=0']]
 rows=[]
 for i,cmd in enumerate(cmds):
  log=HERE/('formal-'+str(i)+'.log');start=time.monotonic()
  with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as f:r=subprocess.run(cmd,cwd=HERE,stdout=f,stderr=subprocess.STDOUT,timeout=60)
  rows.append({'command':cmd,'exitCode':r.returncode,'seconds':time.monotonic()-start,'log':str(log),**stamp(log)})
  if r.returncode:break
 assert sources=={str(p):stamp(p) for p in paths}
 row={'result':'pass' if len(rows)==3 and all(r['exitCode']==0 for r in rows) else 'fail','scope':scope,'checks':rows,'named':45,'samples':2000,'steps':100,'sources':sources,'sourceUnchanged':True,'runtimeApplied':False}
 save(HERE/'formal-before-runtime.json',row);print(json.dumps({'result':row['result'],'report':str(HERE/'formal-before-runtime.json')}));return int(row['result']!='pass')

if __name__=='__main__':raise SystemExit(main())
