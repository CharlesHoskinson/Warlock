"""Formal receipt/queue refinement before QML and runner runtime changes."""
from pathlib import Path
import hashlib,json,os,subprocess
B=Path(__file__).resolve().parent;OLD=B.with_name('toolkit-held-matrix-v14');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=['terminal_drain.py','run_native.py','payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml'];before={n:sha(B/n)for n in files}
records=[];result='pass'
for args in [('typecheck',str(B/'service_terminal_authority.qnt')),('test',str(B/'service_terminal_authority_test.qnt')),('run',str(B/'service_terminal_authority.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1')]:
 p=subprocess.run(['quint',*args],capture_output=True,text=True,timeout=120);records.append(dict(command=['quint',*args],exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr))
 if p.returncode:result='fail';break
row=dict(result=result,named=9,samples=2000,steps=100,serviceGuardStillDraftBeforeCorrection=all(before[n]==sha(B/n)for n in files),sourceHashes=before,records=records,nativeLaunch=False)
fd=os.open(B/'terminal-service-final-formal-before-correction.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in row.items()if k not in ('sourceHashes','records')}));raise SystemExit(result!='pass')
