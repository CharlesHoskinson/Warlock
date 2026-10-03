#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys,json,hashlib,time,os
B=Path(__file__).resolve().parent
job=sys.argv[1];P=B/'proof';P.mkdir(exist_ok=True)
commands=[['quint','typecheck',str(B/f'{job}.qnt')],['quint','test',str(B/f'{job}_test.qnt'),'--max-samples=1'],['quint','run',str(B/f'{job}.qnt'),'--max-samples=2000','--max-steps=100','--invariant=allProps','--n-threads=2']]
if job=='max_pin':commands.append(['quint','run',str(B/f'{job}.qnt'),'--step=validStep','--max-samples=2000','--max-steps=100','--invariant=allProps','--n-threads=2'])
records=[]
for k,args in enumerate(commands):
 log=P/f'{job}-{k}.log';t=time.monotonic();print('START',job,k,flush=True)
 with log.open('xb') as f:r=subprocess.run(args,cwd=B,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 records.append({'argv':args,'exitCode':r.returncode,'elapsedSeconds':time.monotonic()-t,'log':str(log.relative_to(B)),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
 print('DONE',job,k,r.returncode,flush=True)
 if r.returncode:break
(P/f'{job}-commands.json').write_text(json.dumps(records,indent=2)+'\n')
raise SystemExit(any(x['exitCode'] for x in records))
