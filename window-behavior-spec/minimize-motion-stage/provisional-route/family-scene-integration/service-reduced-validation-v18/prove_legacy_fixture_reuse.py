"""Formal accepted fixture model replay before adopting any readiness implementation."""
from pathlib import Path
import hashlib,json,os,subprocess,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent;F=B.with_name('service-recovery-terminal-v17');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
scope=require_qa_scope();assert not (B/'fixture_legacy_ready.py').exists();assert sha(B/'test_renderer_terminal.py')==sha(F/'test_renderer_terminal.py');assert sha(B/'recovery_resources.py')==sha(F/'recovery_resources.py')
before={n:sha(B/n)for n in ('test_renderer_terminal.py','recovery_resources.py','scene_controller.py','scene_manager.py','visual_retirement.py')};records=[]
for args in (['typecheck',str(B/'legacy_fixture_ready_test.qnt')],['test',str(B/'legacy_fixture_ready_test.qnt')],['run',str(B/'legacy_fixture_ready.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']):
 p=subprocess.run(['quint',*args],capture_output=True,text=True,timeout=90);records.append(dict(command=['quint',*args],exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr))
 if p.returncode:break
same=all(sha(B/n)==h for n,h in before.items());passed=len(records)==3 and all(r['exitCode']==0 for r in records) and same
row=dict(result='pass'if passed else 'fail',scope=scope,records=records,sourceSHA256=before,sourceStable=True if same else False,fixtureRuntimeNotYetAdopted=not(B/'fixture_legacy_ready.py').exists(),inheritedEnvironmentGuardExactV17=True,originalV18EnvironmentRefusalCauseUnclassified=True,nativeLaunch=False)
fd=os.open(B/'legacy-fixture-reuse-formal-before-fixture.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps(dict(result=row['result'],named=12,samples=2000,nativeLaunch=False)));raise SystemExit(not passed)
