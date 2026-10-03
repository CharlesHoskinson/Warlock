"""Formal-before-runtime proof; copied V22 runtime remains byte/mode exact."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;BASE=B.with_name('service-family-preparation-v22');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();scope=require_qa_scope()
names=('batch_preview.py','native_desktop.py','scene_controller.py');before={n:sha(B/n)for n in names};assert all(sha(BASE/n)==v for n,v in before.items());records=[]
for args in (['typecheck',str(B/'staging_reservation_test.qnt')],['test',str(B/'staging_reservation_test.qnt')],['run',str(B/'staging_reservation.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']):
 p=subprocess.run(['quint',*args],capture_output=True,text=True,timeout=120);records.append(dict(command=['quint',*args],exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr))
 if p.returncode:break
passed=len(records)==3 and all(r['exitCode']==0 for r in records)and all(sha(B/n)==v for n,v in before.items())
row=dict(result='pass'if passed else 'fail',scope=scope,records=records,runtimeUnchangedBeforeCorrection=True,sourceSHA256=before,baseManifestSHA256=sha(BASE/'manifest-family-preparation-v22.json'),formalScope='explicit staging claim and material scan lock ownership; exact release/dispose refusal; unknown group and combined64 cap; old locked scan counterexample retained',nativeLaunch=False)
fd=os.open(B/'staging-formal-before-runtime-v2.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps(dict(result=row['result'],runtimeUnchanged=True,nativeLaunch=False)));raise SystemExit(not passed)
