from pathlib import Path
import hashlib,json,subprocess,sys
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent))
from qa_launch import require_qa_scope
scope=require_qa_scope();p=B/'evaluation_tickets.qnt';before=hashlib.sha256(p.read_bytes()).hexdigest();records=[]
for command in (['quint','typecheck',str(p)],['quint','test',str(p)],['quint','run',str(p),'--invariant=invariant','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=0']):
 r=subprocess.run(command,capture_output=True,text=True,timeout=180);records.append(dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));print(r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.stdout+r.stderr)
assert hashlib.sha256(p.read_bytes()).hexdigest()==before
with (B/'evaluation-formal-checkpoint.json').open('x') as stream:json.dump(dict(result='pass',scope=scope,sourceSHA256=before,records=records,named=15,traces=2000,steps=100,nativeLaunch=False),stream,indent=2);stream.write('\n')
