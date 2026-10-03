"""Formal exact family expectation proof before correcting the fresh constructor."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;R=B/'retained-before-exact-family-refinement';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();scope=require_qa_scope()
names=('scene_controller.py','scene_manager.py','visual_retirement.py');before={n:sha(B/n)for n in names};assert all(sha(R/n)==v for n,v in before.items());records=[]
for args in (['typecheck',str(B/'retained_family_scope_test.qnt')],['test',str(B/'retained_family_scope_test.qnt')],['run',str(B/'retained_family_scope.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']):
 p=subprocess.run(['quint',*args],capture_output=True,text=True,timeout=90);records.append(dict(command=['quint',*args],exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr))
 if p.returncode:break
passed=len(records)==3 and all(p['exitCode']==0 for p in records)and all(sha(B/n)==v for n,v in before.items())
row=dict(result='pass'if passed else 'fail',scope=scope,records=records,runtimeUnchangedBeforeCorrection=True,sourceSHA256=before,exactTupleSetsNotMemberCounts=True,nativeLaunch=False)
fd=os.open(B/'retained-family-formal-before-runtime-v3.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps(dict(result=row['result'],runtimeUnchanged=True,nativeLaunch=False)));raise SystemExit(not passed)
