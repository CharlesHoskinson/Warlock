from pathlib import Path
import hashlib,json,subprocess,time
from check_source import check,function
B=Path(__file__).resolve().parent
source=check()
qml=(B/'widget_v67/Windows.qml').read_text()
generated=B/'test_actual_lookup_combined.js'
generated.write_text(function(qml,'motionTargetFor')+'\n'+function(qml,'motionTargetObservation')+'\n'+(B/'test_actual_lookup.js').read_text())
binary=B/'test-qjs'
build=['/usr/bin/clang++','-std=c++20','-MD','-MF',str(B/'test-qjs.d'),str(B/'test_qjs.cpp'),'-o',str(binary)]
flags=subprocess.run(['pkg-config','--cflags','--libs','Qt6Qml','Qt6Core'],capture_output=True,text=True,check=True).stdout.split()
commands=[build+flags,[str(binary),str(B/'widget_v67/MotionTargets.js'),str(B/'test_motion_targets.js')],[str(binary),str(B/'widget_v67/MotionTargets.js'),str(generated)],['quint','test',str(B/'motion_targets.qnt')],['quint','run',str(B/'motion_targets.qnt'),'--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=20261002','--verbosity=1']]
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in B.rglob('*')if p.is_file()and p.name not in('offline-report.json','test-qjs','test-qjs.d')and not p.name.startswith('offline-failure-')and '__pycache__'not in p.parts}
rows=[]
for c in commands:
 r=subprocess.run(c,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 if r.returncode:break
ok=len(rows)==len(commands)and all(r['returncode']==0 for r in rows)
row=dict(result='pass'if ok else'fail',sourceReview=source,commands=rows,sourceSHA256=before,sourceUnchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in before.items()),nativeExecuted=False,GUIAcceptance=False,latencyAcceptance=False)
p=B/('offline-report.json'if ok else f'offline-failure-{time.time_ns()}.json');p.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row));raise SystemExit(not ok)
