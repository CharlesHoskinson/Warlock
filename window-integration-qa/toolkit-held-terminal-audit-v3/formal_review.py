import json,hashlib,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;scope=require_qa_scope();records=[]
for command in [['quint','typecheck',str(B/'wheel_input.qnt')],['quint','test',str(B/'wheel_input_test.qnt')],['quint','run',str(B/'wheel_input.qnt'),'--invariant=invariant','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]:
 r=subprocess.run(command,text=True,capture_output=True,timeout=120);records.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 if r.returncode:break
result='pass' if len(records)==3 and all(r['returncode']==0 for r in records) else 'fail'
with (B/'formal-before-runtime.json').open('x') as f:json.dump(dict(result=result,scope=scope,commands=records,nativeLaunch=False,runtimeImplemented=False,sources={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [B/'CONTRACT.md',B/'wheel_input.qnt',B/'wheel_input_test.qnt']}),f,indent=2);f.write('\n')
print(result);raise SystemExit(int(result!='pass'))
