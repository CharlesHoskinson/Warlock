import subprocess,json,time,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent;n=p/'native-candidate'
files=list(n.glob('*.cpp'))+list(n.glob('*.hpp'))+[n/'Makefile']
hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest()for f in files}
rows=[]
c=['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fPIC','-O2','-MD','-MF',str(n/'pinBridge-v25.d')]
c+=subprocess.check_output(['pkg-config','--cflags','hyprland','cairo','json-c','libeis-1.0'],text=True).split()
c+=['-c',str(n/'pinBridge.cpp'),'-o',str(n/'pinBridge-v25.o')]
for command in [c,['/usr/bin/g++','-std=c++23','-Wall','-Wextra','-Werror','-pedantic',str(p/'test_pin_stacking.cpp'),'-o',str(p/'test-pin-stacking')],[str(p/'test-pin-stacking')]]:
 r=subprocess.run(command,cwd=n,capture_output=True,text=True,timeout=240);rows.append(dict(command=command,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 if r.returncode:break
ok=all(r['returncode']==0 for r in rows)
record=dict(result='pass'if ok else'fail',commands=rows,sourceSHA256=hashes,sourceUnchanged=all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in hashes.items()),nativeExecuted=False,mainWrites=False)
path=p/('pin-v25-strict-cpu-checkpoint.json'if ok else f'pin-v25-strict-failure-{time.time_ns()}.json');path.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(result=record['result'],sourceUnchanged=record['sourceUnchanged'],artifact=str(path),logs=[r['stdout']+r['stderr']for r in rows])));raise SystemExit(not ok)
