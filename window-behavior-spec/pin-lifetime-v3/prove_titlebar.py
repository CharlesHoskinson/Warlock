from pathlib import Path
import hashlib,json,subprocess,time
B=Path(__file__).resolve().parent
sources=[B/'pin_titlebar.qnt',B/'TITLEBAR_PIN_CONTRACT.md',B/'native-candidate/barDeco.cpp']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in sources}
commands=[['quint','test',str(B/'pin_titlebar.qnt')],['quint','run',str(B/'pin_titlebar.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']]
rows=[]
for c in commands:
 r=subprocess.run(c,capture_output=True,text=True,timeout=90);rows.append(dict(command=c,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
ok=all(r['returncode']==0 for r in rows)
row=dict(result='pass'if ok else'fail',commands=rows,sourceSHA256=before,sourceUnchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items()),reservedEarlyRouteAbsent='Reserved Pin is captured before'not in(B/'native-candidate/barDeco.cpp').read_text(),nativeExecuted=False)
p=B/('titlebar-formal-before-implementation.json'if ok else f'titlebar-model-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],artifact=str(p),logs=[r['stdout']+r['stderr']for r in rows])));raise SystemExit(not ok)
