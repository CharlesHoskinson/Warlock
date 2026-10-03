from pathlib import Path
import subprocess,json,hashlib,time
p=Path(__file__).resolve().parent
commands=[['quint','test',str(p/'pin_focus.qnt')],['quint','run',str(p/'pin_focus.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]
rows=[]
for c in commands:
 r=subprocess.run(c,capture_output=True,text=True,timeout=90);rows.append(dict(command=c,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
ok=all(r['returncode']==0 for r in rows)
r=dict(result='pass'if ok else'fail',commands=rows,sourceSHA256={n:hashlib.sha256((p/n).read_bytes()).hexdigest()for n in ['pin_focus.qnt','FOCUS_PRESERVATION_CONTRACT.md']},implementationUnchanged=True,nativeExecuted=False)
f=p/('focus-formal-before-implementation.json'if ok else f'focus-model-failure-{time.time_ns()}.json');f.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));raise SystemExit(not ok)
