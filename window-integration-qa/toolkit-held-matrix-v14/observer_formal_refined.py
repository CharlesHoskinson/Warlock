from pathlib import Path
import json,hashlib,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;scope=require_qa_scope();records=[]
for command in [['quint','typecheck',str(B/'delegate_observer.qnt')],['quint','test',str(B/'delegate_observer_test.qnt')],['quint','run',str(B/'delegate_observer.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]:
 r=subprocess.run(command,capture_output=True,text=True,timeout=120);records.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 if r.returncode:break
result='pass' if len(records)==3 and all(r['returncode']==0 for r in records) else 'fail'
with (B/'observer-formal-refined-before-runtime.json').open('x') as f:json.dump(dict(result=result,scope=scope,commands=records,nativeLaunch=False,runtimeImplemented=False,sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [B/'DELEGATE_OBSERVER_CONTRACT.md',B/'delegate_observer.qnt',B/'delegate_observer_test.qnt']}),f,indent=2);f.write('\n')
print(result);raise SystemExit(int(result!='pass'))
