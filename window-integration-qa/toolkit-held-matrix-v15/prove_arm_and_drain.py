"""Formal proof before runtime/QML changes; scoped CPU only."""
from pathlib import Path
import hashlib,json,subprocess,os
B=Path(__file__).resolve().parent;OLD=B.with_name('toolkit-held-matrix-v14');records=[]
files=['evaluation_setup.py','run_native.py','qs_lifecycle.py','helper_setup.py','helper_observer.py','private_shell.py','payload-manifest.json','payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={n:sha(B/n)for n in files};assert all((B/n).read_bytes()==(OLD/n).read_bytes()for n in files)
result='pass'
for name in ('arm_publication','terminal_query_drain'):
 for args in [('typecheck',str(B/(name+'.qnt'))),('test',str(B/(name+'_test.qnt'))),('run',str(B/(name+'.qnt')),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1')]:
  command=['quint',*args];p=subprocess.run(command,capture_output=True,text=True,timeout=120);records.append(dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr))
  if p.returncode:result='fail';break
 if result!='pass':break
row=dict(result=result,named=29,models=2,samplesPerModel=2000,steps=100,runtimeUnchangedExactV14=all(before[n]==sha(B/n)for n in files),runtimeHashes=before,records=records,nativeLaunch=False,nativeLoaded=False)
fd=os.open(B/'arm-drain-formal-before-runtime.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in row.items()if k not in ('records','runtimeHashes')}));raise SystemExit(result!='pass')
