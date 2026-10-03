import hashlib,json,subprocess,time
from pathlib import Path
p=Path(__file__).resolve().parent
rows=[]
for command in [['quint','test',str(p/'pin_stacking_test.qnt')],['quint','run',str(p/'pin_stacking.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1'],['quint','test',str(p/'pin_frontend_test.qnt')],['quint','run',str(p/'pin_frontend.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261001','--verbosity=1']]:
 r=subprocess.run(command,capture_output=True,text=True,timeout=90);rows.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
ok=all(r['returncode']==0 for r in rows)
report=dict(result='pass' if ok else 'fail',commands=rows,sourceSHA256={str(p/n):hashlib.sha256((p/n).read_bytes()).hexdigest()for n in ['pin_stacking.qnt','pin_stacking_test.qnt','pin_frontend.qnt','pin_frontend_test.qnt','STACKING_FRONTEND_CONTRACT.md']},newStackImplementationAbsent=not(p/'native-candidate/PinStacking.hpp').exists(),lowerHookImplementationAbsent='lowerHook ='not in(p/'native-candidate/familyBridge.cpp').read_text(),frontendImplementationAbsent=not(p/'frontend').exists(),nativeExecuted=False)
path=p/('stack-formal-before-implementation.json'if ok else f'stack-model-failure-{time.time_ns()}.json');path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(result=report['result'],path=str(path),logs=[r['stdout']+r['stderr']for r in rows])));raise SystemExit(not ok)
