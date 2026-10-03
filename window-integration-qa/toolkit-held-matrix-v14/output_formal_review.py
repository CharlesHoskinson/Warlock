from pathlib import Path
import hashlib,json,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
scope=require_qa_scope();records=[]
for command in [['quint','typecheck',str(B/'output_readiness.qnt')],['quint','test',str(B/'output_readiness_test.qnt')],['quint','run',str(B/'output_readiness.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]:
 r=subprocess.run(command,capture_output=True,text=True,timeout=120);records.append(dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 if r.returncode:break
sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'run_native.py',B/'output_readiness.qnt',B/'output_readiness_test.qnt',B/'OUTPUT_READINESS_CONTRACT.md')}
result='pass' if len(records)==3 and all(r['exitCode']==0 for r in records) else 'fail'
p=B/'output-formal-before-runtime.json'
with p.open('x') as f:json.dump(dict(result=result,scope=scope,commands=records,sources=sources,nativeLaunch=False,runtimeChanged=False),f,indent=2);f.write('\n')
p.chmod(0o600);print(result);raise SystemExit(int(result!='pass'))
