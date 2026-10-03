from pathlib import Path
import hashlib,json,subprocess,time
B=Path(__file__).resolve().parent
files=[B/'frontend_case.qnt',B/'FRONTEND_OBSERVATION_CONTRACT.md']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
commands=[['quint','test',str(B/'frontend_case.qnt')],['quint','run',str(B/'frontend_case.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']]
rows=[]
for c in commands:
 r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
ok=all(r['returncode']==0 for r in rows)
row=dict(result='pass'if ok else'fail',commands=rows,sourceSHA256=before,sourceUnchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items()),controllerAbsent=not(B/'frontend_cases.py').exists(),nativeExecuted=False)
p=B/('frontend-formal-before-controller.json'if ok else f'frontend-model-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row));raise SystemExit(not ok)
