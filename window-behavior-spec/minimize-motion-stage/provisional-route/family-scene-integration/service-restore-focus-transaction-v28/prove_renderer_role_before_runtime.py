from pathlib import Path
import hashlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();B=Path(__file__).resolve().parent;BASE=B.with_name('service-family-preparation-v23');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
names=('batch_preview.py','native_runtime.py','scene_controller.py','helper_supervisor.py','owned_launch.py','pipe_transport.py','owned_commands.py');before={n:sha(B/n)for n in names};assert all(sha(BASE/n)==h for n,h in before.items())
checks=[]
for args in (['typecheck',str(B/'renderer_job_role_test.qnt')],['test',str(B/'renderer_job_role_test.qnt')],['run',str(B/'renderer_job_role.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=2026100703','--verbosity=1']):
 p=subprocess.run(['quint',*args],capture_output=True,text=True,timeout=120);checks.append(dict(command=['quint',*args],exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr))
 if p.returncode:break
ok=len(checks)==3 and all(c['exitCode']==0 for c in checks)and all(sha(B/n)==h for n,h in before.items())
row=dict(result='pass'if ok else'fail',scope=scope,checks=checks,namedCases=36,samples=2000,steps=100,runtimeUnchanged=True,runtimeBeforeSHA256=before,baseManifestSHA256=sha(BASE/'manifest-family-preparation-v23.json'),modelSHA256={n:sha(B/n)for n in ('renderer_job_role.qnt','renderer_job_role_test.qnt','RENDERER_JOB_ROLE_CONTRACT.md')},nativeLaunch=False)
with os.fdopen(os.open(B/'renderer-role-formal-before-runtime-v3.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in row.items()if k not in('checks','modelSHA256','runtimeBeforeSHA256')}));raise SystemExit(not ok)
