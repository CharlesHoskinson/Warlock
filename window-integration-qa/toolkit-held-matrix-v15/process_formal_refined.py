from pathlib import Path
import hashlib,json,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
scope=require_qa_scope();records=[]
for command in [['quint','typecheck',str(B/'process_observation.qnt')],['quint','test',str(B/'process_observation_test.qnt')],['quint','run',str(B/'process_observation.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]:
 r=subprocess.run(command,capture_output=True,text=True,timeout=120);records.append(dict(command=command,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 if r.returncode:break
sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'helper_observer.py',B/'process_observation.qnt',B/'process_observation_test.qnt',B/'PROCESS_OBSERVATION_CONTRACT.md')}
result='pass' if len(records)==3 and all(r['exitCode']==0 for r in records) else 'fail'
p=B/'process-formal-refined-before-runtime.json'
with p.open('x') as f:json.dump(dict(result=result,scope=scope,commands=records,sources=sources,nativeLaunch=False,runtimeChanged=False),f,indent=2);f.write('\n')
p.chmod(0o600);print(result);raise SystemExit(int(result!='pass'))
