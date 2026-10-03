from pathlib import Path
import hashlib,json,subprocess,sys,os
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent))
from qa_launch import require_qa_scope
scope=require_qa_scope();model=B/'evaluation_tickets.qnt';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();before=sha(model);records=[]
for command in (['quint','typecheck',str(model)],['quint','test',str(model)],['quint','run',str(model),'--invariant=invariant','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']):
 r=subprocess.run(command,capture_output=True,text=True,timeout=180);records.append(dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));print(r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.stdout+r.stderr)
assert sha(model)==before
runtime={name:sha(B/name) for name in ('helper_observer.py','helper_setup.py','evaluation_setup.py','held_route.py','run_native.py','held_controller.py','observations.py')}
assert all(sha(B.parent/'toolkit-held-matrix-v7'/name)==value for name,value in runtime.items())
fd=os.open(B/'boundary-formal-checkpoint.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
with os.fdopen(fd,'w') as stream:json.dump(dict(result='pass',scope=scope,sourceSHA256=before,records=records,named=21,traces=2000,steps=100,runtimeExactFrozenV7=runtime,nativeLaunch=False,mainWrites=False,rootReviewPending=True),stream,indent=2);stream.write('\n')
