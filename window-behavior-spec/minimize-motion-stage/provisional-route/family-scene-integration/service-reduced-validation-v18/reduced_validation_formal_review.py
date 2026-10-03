from pathlib import Path
import hashlib,json,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;scope=require_qa_scope();records=[]
for command in [['quint','typecheck',str(B/'reduction_validation_v18.qnt')],['quint','test',str(B/'reduction_validation_v18_test.qnt')],['quint','run',str(B/'reduction_validation_v18.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]:
 result=subprocess.run(command,capture_output=True,text=True,timeout=120);records.append(dict(command=command,exitCode=result.returncode,stdout=result.stdout,stderr=result.stderr))
 if result.returncode:break
initial=json.loads((B/'formal-initial-source-epoch.json').read_text());unchanged=all(hashlib.sha256((B/name).read_bytes()).hexdigest()==value for name,value in initial['sources'].items());passed=len(records)==3 and all(r['exitCode']==0 for r in records) and unchanged
report=dict(result='pass' if passed else 'fail',scope=scope,commands=records,runtimeUnchangedV17=unchanged,sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (B/'REDUCTION_VALIDATION_CONTRACT.md',B/'reduction_validation_v18.qnt',B/'reduction_validation_v18_test.qnt')},noNative=True,runtimeImplemented=False)
p=B/'reduced-validation-formal-before-runtime.json'
with p.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
p.chmod(0o600);print(report['result']);raise SystemExit(int(not passed))
